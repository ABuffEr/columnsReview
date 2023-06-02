# -*- coding: UTF-8 -*-
# ColumnsReview
# A global plugin for NVDA
# Copyright 2014 Alberto Buffolino, released under GPL
# Add-on to manage columns in list views
# Code inspired by EnhancedListViewSupport plugin,
# by Peter Vagner and contributors
# Many thanks to Robert Hänggi and Abdelkrim Bensaïd
# for shell code suggestions,
# to Noelia Ruiz Martínez
# for original selected items feature,
# to Cyrille Bougot
# for suggestions and sysListView32 threading support,
# and to other users of NVDA mailing lists
# for feedback and comments

from displayModel import DisplayModelTextInfo
import textInfos
from logHandler import log
from NVDAObjects.IAccessible import getNVDAObjectFromEvent
from NVDAObjects.IAccessible import sysListView32
from NVDAObjects.UIA import UIA # For UIA implementations only, chiefly 64-bit.
import sys
from comtypes.client import CreateObject
from comtypes.gen.IAccessible2Lib import IAccessible2
from globalCommands import commands
from oleacc import STATE_SYSTEM_MULTISELECTABLE, SELFLAG_TAKEFOCUS, SELFLAG_TAKESELECTION, SELFLAG_ADDSELECTION
from scriptHandler import getLastScriptRepeatCount
import weakref
from threading import Thread, Event
from time import sleep
from tones import beep
import addonHandler
import api
import braille
import config
import core
import ctypes
import cursorManager
import eventHandler
import globalPluginHandler
import globalVars
import gui
import locale
import speech
import ui
import UIAHandler
import watchdog
import winUser
import wx
from _ctypes import COMError
import inspect

from .actions import ACTIONS, actionFromName, configuredActions
from .commonFunc import NVDALocale, findAllDescendantWindows, getScriptGestures
from .compat import CTWRAPPER, rangeFunc
from . import configManager
from . import configSpec
from . import dialogs
from .exceptions import columnAtIndexNotVisible, noColumnAtIndex
from . import utils

# rename for code clarity
SysLV32List = sysListView32.List
roles = CTWRAPPER.Role
states = CTWRAPPER.State
py3 = sys.version.startswith("3")
config.conf.spec["columnsReview"] = configSpec.confspec

addonHandler.initTranslation()

# useful in ColumnsReview64 to calculate file size
getBytePerSector = ctypes.windll.kernel32.GetDiskFreeSpaceW
PROFILE_SWITCHED_NOTIFIERS = ("configProfileSwitch", "post_configProfileSwitch")
# for debug logging
DEBUG = False

def debugLog(message):
	if DEBUG:
		log.info(message)

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		if globalVars.appArgs.secure:
			return
		self.createMenu()
		self.proceedWithBounds = False
		for extPointName in PROFILE_SWITCHED_NOTIFIERS:
			try:
				getattr(config, extPointName).register(self.handleConfigProfileSwitch)
			except AttributeError:
				continue

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		objRole = obj.role
		objWindowClassName = obj.windowClassName
		if objRole == roles.LIST:
			if SysLV32List in clsList:
				clsList.insert(0, CRList32)
			# Windows 8/8.1/10 Start Screen tiles should not expose column info.
			elif UIA in clsList and obj.UIAElement.cachedClassName == "UIItemsView":
				clsList.insert(0, CRList64)
			return
		# for Outlook
		if (
			objRole == roles.TABLE
			and UIA in clsList
			and obj.UIAElement.cachedClassName == "SuperGrid"
		):
			clsList.insert(0, UIASuperGrid)
			return
		if (
			objRole in (roles.TABLE, roles.TREEVIEW)
			and objWindowClassName == "MozillaWindowClass"
			and "id:threadTree" in obj.IAccessibleObject.attributes
		):
			clsList.insert(0, MozillaTable)
			return
		# found in RSSOwlnix, but may be in other software
		if objRole == roles.TREEVIEW:
			try:
				watchdog.alive()
				if obj.parent.previous.windowClassName == "SysHeader32":
					clsList.insert(0, CRTreeview)
			except AttributeError:
				pass

	def event_focusEntered(self, obj, nextHandler):
		if (
			obj.role == roles.LIST
			or (obj.role == roles.TABLE and obj.windowClassName == "MozillaWindowClass")
		):
			self.proceedWithBounds = True
		else:
			self.proceedWithBounds = False
		nextHandler()

	def event_gainFocus(self, obj, nextHandler):
		# speedup: nothing for web
		if obj.treeInterceptor:
			nextHandler()
			return
		if (
			self.proceedWithBounds
			and (obj.role == roles.LISTITEM
				or (obj.role == roles.TABLEROW and obj.windowClassName == "MozillaWindowClass")
			)
		):
			self.reportListBounds(obj)
#		debugLog("Running event_gainFocus nextHandler")
		nextHandler()
#		debugLog("Finished Running event_gainFocus nextHandler")

	def reportListBounds(self, obj):
		positionInfo = obj._get_positionInfo()
		if not positionInfo:
			return
		pos = None
		index = positionInfo.get("indexInGroup")
		similar = positionInfo.get("similarItemsInGroup")
		if index == similar == 1:
			pos = "mono"
		elif index == similar != None:
			pos = "bottom"
		elif index == 1:
			pos = "top"
		if not pos:
			return
		confFromObj = configManager.ConfigFromObject(obj)
		if not confFromObj.announceListBounds:
			return
		reportFunc = speech.speakMessage if confFromObj.announceListBoundsWith == "voice" else beep
		if reportFunc is beep:
			topBeep = confFromObj.topBeep
			bottomBeep = confFromObj.bottomBeep
			beepLen = confFromObj.beepLen
		if pos == "mono":
			# Translators: message when list contains one item only
			message = (_("Mono-item list: "),) if reportFunc != beep else (abs(topBeep-bottomBeep), beepLen*2,)
		elif pos == "bottom":
			# Translators: message when user lands on the last list item
			message = (_("List bottom: "),) if reportFunc != beep else (topBeep, beepLen,)
		elif pos == "top":
			# Translators: message when user lands on the first list item
			message = (_("List top: "),) if reportFunc != beep else (bottomBeep, beepLen,)
		reportFunc(*message)

	def createMenu(self):
		# Dialog or the panel.
		if hasattr(gui.settingsDialogs, "SettingsPanel"):
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(
				dialogs.ColumnsReviewSettingsDialog
			)
		else:
			self.prefsMenu = gui.mainFrame.sysTrayIcon.menu.GetMenuItems()[0].GetSubMenu()
			# Translators: menu item in preferences
			self.ColumnsReviewItem = self.prefsMenu.Append(wx.ID_ANY, _("Columns Review Settings..."), "")
			gui.mainFrame.sysTrayIcon.Bind(
				wx.EVT_MENU,
				lambda e: gui.mainFrame._popupSettingsDialog(dialogs.ColumnsReviewSettingsDialog),
				self.ColumnsReviewItem
			)

	def terminate(self):
		for extPointName in PROFILE_SWITCHED_NOTIFIERS:
			try:
				getattr(config, extPointName).unregister(self.handleConfigProfileSwitch)
			except AttributeError:
				continue
		if hasattr(gui.settingsDialogs, "SettingsPanel"):
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(
				dialogs.ColumnsReviewSettingsDialog
			)
		else:
			try:
				self.prefsMenu.RemoveItem(self.ColumnsReviewItem)
			except wx.PyDeadObjectError:
				pass
		# release COM object
		if CRList64.shell:
			CRList64.shell.Release()
			del CRList64.shell

	def handleConfigProfileSwitch(self):
		# We cannot iterate through original set of instances
		# since it may be mutated during iteration when new objects are created as a result of focus events.
		for inst in CRList._instances.copy():
			inst.bindCRGestures(reinitializeObj=True)


class CRList(object):
	"""The main abstract class that generates gestures and calculate index;
	classes that define new list types must override it,
	defining (or eventually re-defining) methods of this class."""

	# Translators: Name of the default category
	# in the Input Gestures dialog where scripts of this add-on are placed.
	scriptCategory = _('{name} (DO NOT EDIT!)').format(name=addonHandler.getCodeAddon().manifest['summary'])

	_instances = weakref.WeakSet()
	# the variable representing tens
	# of current interval (except the last column,
	# for which it's tens+1)
	tens = 0
	# the variable which keeps track of the last chosen column number
	lastColumn = None
	# search parameter variables
	_lastCaseSensitivity = False
	# compatibility code before/after search history introduction
	if hasattr(cursorManager, "SEARCH_HISTORY_MOST_RECENT_INDEX"):
		SEARCH_HISTORY_MOST_RECENT_INDEX = 0
		SEARCH_HISTORY_LEAST_RECENT_INDEX = 19
		_searchEntries = []
	else:
		_lastFindText = ""
	# Should next presses of the command to read column be executed?
	shouldExecuteNextPresses = True
	# Keeps track of how many times the given command has been pressed
	repeatCount = 0
	# Set to `True` if the particular class should behave differently when the list is empty.
	# Don't forget to implement `isEmptyList` for the class if this is set to `True`.
	supportsEmptyListAnnouncements = False

	def initOverlayClass(self):
		"""adds the new objects to the list of existing instances"""
		self.__class__._instances.add(self)

	def event_focusEntered(self):
		super(CRList, self).event_focusEntered()
		self.bindCRGestures()
		beep(120, 100)

	def bindCRGestures(self, reinitializeObj=False):
		if reinitializeObj:
			self.clearGestureBindings()
		if self.supportsEmptyListAnnouncements and self.isEmptyList():
			self.handleEmpty()
			return
		# find gestures
		self.bindGesture("kb:NVDA+control+f", "find")
		self.bindGesture("kb:NVDA+f3", "findNext")
		self.bindGesture("kb:NVDA+shift+f3", "findPrevious")
		# other useful gesture to remap
		scriptMap = {
			# for color reporting
			getattr(commands, "script_reportOrShowFormattingAtCaret", commands.script_reportFormatting): "reportOrShowFormattingAtCaret",
			# for current selection
			commands.script_reportCurrentSelection: "reportCurrentSelection",
		}
		# for say all - bind only if it is actually supported
		if utils._RowsReader.isSupported():
			scriptMap[commands.script_sayAll] = "readListItems"
		scriptFuncs = scriptMap.keys()
		scriptGesturesMap = getScriptGestures(*scriptFuncs)
		for scriptFunc, gestures in scriptGesturesMap.items():
			for gesture in gestures:
				self.bindGesture(gesture, scriptMap[scriptFunc])
		confFromObj = configManager.ConfigFromObject(self)
		numpadUsedForColumnNav = confFromObj.numpadUsedForColumnsNavigation
		enabledModifiers = confFromObj.enabledModifiers
		# a string useful for defining gestures
		nk = "numpad" if numpadUsedForColumnNav else ""
		# bind gestures from 1 to 9
		for n in rangeFunc(1, 10):
			self.bindGesture("kb:{0}+{1}{2}".format(enabledModifiers, nk, n), "readColumn")
		if numpadUsedForColumnNav:
			# map numpadMinus for 10th column
			self.bindGesture("kb:{0}+numpadMinus".format(enabledModifiers), "readColumn")
			# ...numpadPlus to change interval
			self.bindGesture("kb:{0}+numpadPlus".format(enabledModifiers), "changeInterval")
			# delete for list item info
			self.bindGesture("kb:{0}+numpadDelete".format(enabledModifiers), "itemInfo")
			# ...and enter to headers manager
			self.bindGesture("kb:{0}+numpadEnter".format(enabledModifiers), "manageHeaders")
		else:
			# do same things for no numpad case
			self.bindGesture("kb:{0}+0".format(enabledModifiers), "readColumn")
			self.bindGesture("kb:{0}+{1}".format(enabledModifiers, confFromObj.nextColumnsGroupKey), "changeInterval")
			self.bindGesture("kb:{0}+delete".format(enabledModifiers), "itemInfo")
			self.bindGesture("kb:{0}+enter".format(enabledModifiers), "manageHeaders")

	def getColumnData(self, colNumber):
		"""Returs information about the column at the index given as  parameter.
		Raises exceptions if the column at the given index does not exist, or is not visible.
		On success returns dictionary containing columnContent and columnHeader as keys,
		and the actual info as values.
		"""
		raise NotImplementedError

	def script_readColumn(self, gesture):
		# ask for index
		num = self.getIndex(gesture.mainKeyName.rsplit('+', 1)[-1])
		repeatCount = getLastScriptRepeatCount()
		if not repeatCount:
			self.repeatCount = 0
			self.lastColumn = num
			self.shouldExecuteNextPresses = True
		if not self.shouldExecuteNextPresses:
			return
		if num != self.lastColumn:
			self.lastColumn = num
			self.repeatCount = 1
		else:
			self.repeatCount += 1
		actionToExecute = configuredActions().get(
			self.repeatCount,
			ACTIONS[0].name  # Default dummy action
		)
		actionToExecute = actionFromName(actionToExecute)
		if not actionToExecute.performsAction:
			return
		self.shouldExecuteNextPresses = actionToExecute.showLaterActions
		try:
			columnData = self.getColumnData(num)
		except noColumnAtIndex:
			# Translators: message when digit pressed exceed the columns number
			ui.message(_("No more columns available"))
			return
		except columnAtIndexNotVisible:
			# Translators: Announced when the column at the requested index is not visible.
			ui.message(_("No more visible columns available"))
			return
		columnContent = columnData["columnContent"]
		columnHeader = columnData["columnHeader"]
		if not columnContent and not columnHeader:
			ui.message(_("Empty column"))
			return
		actionToExecute(columnContent, columnHeader)

	script_readColumn.canPropagate = True
	script_readColumn.__doc__ = _(
		# Translators: documentation of script to read columns
		"Returns the header and the content of the list column at the index corresponding to the number pressed"
	)

	def getIndex(self, key):
		"""get index from key pressed"""
		if key == "numpadMinus":
			# we assume minus as 0 for a comfortable use
			key = "0"
		# get the digit pressed as index
		num = int(key[-1])
		# if num == 0, from numpad or keyboard
		if not num:
			# set it to 10, 20, etc
			num = (self.tens+1)*10
		else:
			# set it to 9, 13, 22, etc
			num = self.tens*10+num
		return num

	def script_changeInterval(self, gesture):
		"""controls the grow of tens variable,
		it's built so to have always all gestures from 1 to 0"""
		curItem = api.getFocusObject()
		# no further interval
		if curItem.childCount<10:
			# Translators: message when digit pressed exceed the columns number
			ui.message(_("No more columns available"))
			return
		# in a list with 13 columns (childCount == 13),
		# childCount/10+1 (integer operation) gives all
		# intervals (2) of needed  10 columns;
		# if childCount is a multiple of 10 (es. 30),
		# we have exactly childCount/10=3 intervals.
		mod = curItem.childCount//10+(1 if curItem.childCount%10 else 0)
		# now, we can scroll ten by ten among intervals, using modulus
		self.tens = (self.tens+1)%mod
		# interval bounds to announce
		start = self.tens*10+1
		# nice: announce what is the absolutely last column available
		if self.tens == mod-1:
			end = curItem.childCount
		else:
			end = (self.tens+1)*10
		# Translators: message when you change interval in a list with more ten columns
		ui.message(_("From {start} to {end}").format(start=start, end=end))

	script_changeInterval.canPropagate = True
	script_changeInterval.__doc__ = _(
		# Translators: documentation for script to change interval
		"Cycles between a variable number of intervals of ten columns"
	)

	def script_itemInfo(self, gesture):
		curItem = api.getFocusObject()
		number = total = None
		try:
			number = curItem.positionInfo["indexInGroup"]
			total = curItem.positionInfo["similarItemsInGroup"]
		except (AttributeError, KeyError):
			tempList = [i for i in self.children if i.role == roles.LISTITEM]
			if tempList:
				number = tempList.index(curItem)
				total = len(tempList)
		if None in (number, total):
			# Translators: Reported when information about position on a list cannot be retrieved.
			ui.message(_("No information available"))
		else:
			info = ' '.join([NVDALocale("item"), NVDALocale("{number} of {total}").format(number=number, total=total)])
			ui.message(info)

	script_itemInfo.canPropagate = True
	script_itemInfo.__doc__ = _(
		# Translators: documentation for script to announce list item info
		"Announces list item position information"
	)

	def script_manageHeaders(self, gesture):
		headers = [h for h in self.getHeaderParent().children if states.INVISIBLE not in h.states]
		wx.CallAfter(
			dialogs.HeaderDialog.Run,
			title=self.appModule.appName,
			headerList=headers
		)

	script_manageHeaders.canPropagate = True
	script_manageHeaders.__doc__ = _(
		# Translators: documentation for script to manage headers
		"Provides a dialog for interactions with list column headers"
	)

	def getHeaderParent(self):
		"""return the navigator object with header objects as children."""
		raise NotImplementedError

	def getSelectedItems(self):
		"""Returns names of currently selected list items as a list of strings
		or None if selected items cannot be retrieved.
		"""
		# generic (slow) implementation
		# (actually not used by any subclass)
		curItem = api.getFocusObject()
		items = []
		item = self.firstChild
		while (item and item.role == curItem.role):
			if states.SELECTED in item.states:
				itemChild = item.getChild(0)
				itemName = itemChild.name if itemChild else item.name
				if itemName:
					items.append(itemName)
			item = item.next
		return items

	def script_reportCurrentSelection(self, gesture):
		items = self.getSelectedItems()
		if items is not None:
			ui.message(_(
				# Translators: message presented when get selected item count and names
				"{selCount} selected items: {selNames}").format(selCount=len(items), selNames=', '.join(items)
			))

	script_reportCurrentSelection.canPropagate = True
	script_reportCurrentSelection.__doc__ = _(
		# Translators: documentation for script to know current selected items
		"Reports current selected list items"
	)

	def script_find(self, gesture, reverse=False):
		self.searchFromItem = api.getFocusObject()
		if hasattr(cursorManager, "SEARCH_HISTORY_MOST_RECENT_INDEX"):
			d = FindDialog(gui.mainFrame, self, self._lastCaseSensitivity, self._searchEntries, reverse)
		else:
			try:
				d = FindDialog(gui.mainFrame, self, self._lastFindText, self._lastCaseSensitivity, reverse)
			except:
				# until NVDA 2020.3
				d = FindDialog(gui.mainFrame, self, self._lastFindText, self._lastCaseSensitivity)
		gui.mainFrame.prePopup()
		d.Show()
		gui.mainFrame.postPopup()

	script_find.canPropagate = True
	script_find.__doc__ = _(
		# Translators: documentation for script to find in list
		"Provides a dialog for searching in item list"
	)

	def doFindText(self, text, reverse=False, caseSensitive=False):
		"""manages actions pre and post search."""
		if not text:
			return
		speech.cancelSpeech()
		# Translators: Message presented when search is in progress.
		msgArgs = [_("Searching...")]
		try:
			from speech.priorities import SpeechPriority
			msgArgs.append(SpeechPriority.NOW)
		except ImportError:  # NVDA 2019.2.1 or earlier - no priorities in speech.
			pass
		ui.message(*msgArgs)
		if self.THREAD_SUPPORTED:
			# Call launchFinder asynchronously, i.e. without expecting it to return
			Thread(target=self.launchFinder, args=(text, reverse, caseSensitive) ).start()
		else:
			res = self.findInList(text, reverse, caseSensitive)
			speech.cancelSpeech()
			if res:
				self.successSearchAction(res)
			else:
				wx.CallAfter(gui.messageBox, NVDALocale('text "%s" not found')%text, NVDALocale("Find Error"), wx.OK|wx.ICON_ERROR)
		CRList._lastFindText = text
		CRList._lastCaseSensitivity = caseSensitive

	def launchFinder(self, text, reverse, caseSensitive):
		global gFinder
		if gFinder is not None:
			gFinder.stop()
		gFinder = Finder(self, text, reverse, caseSensitive)
		# Create local ref to finder. Local ref should be used during this whole function execution, while global ref may be deleted or overridden.
		finder = gFinder
		finder.start()
		i = 0
		while finder.isAlive():
			sleep(0.1)
			i += 1
			if i == 10:
				beep(500, 100)
				i = 0
		finder.join()
		if finder.status == Finder.STATUS_COMPLETE:
			if finder.res:
				core.callLater(0, self.successSearchAction, finder.res)
			else:
				wx.CallAfter(gui.messageBox, NVDALocale('text "%s" not found')%text, NVDALocale("Find Error"), wx.OK|wx.ICON_ERROR)
		else:
			core.callLater(0, beep, 220, 150 )
		finder = None

	def findInList(self, text, reverse, caseSensitive, stopCheck=lambda:False):
		"""performs the search in item list, via NVDA object navigation."""
		# generic implementation
		curItem = self.searchFromItem
		item = curItem.previous if reverse else curItem.next
		while (item and item.role == curItem.role):
			if (
				(not caseSensitive and item.name and text.lower() in item.name.lower())
				or
				(caseSensitive and text in item.name)
			):
				return item
			item = item.previous if reverse else item.next
			if stopCheck():
				break

	def isMultipleSelectionSupported(self):
		raise NotImplementedError

	def successSearchAction(self, res):
		raise NotImplementedError

	def script_findNext(self, gesture):
		if not self._lastFindText:
			self.script_find(gesture)
			return
		self.searchFromItem = api.getFocusObject()
		self.doFindText(self._lastFindText, caseSensitive = self._lastCaseSensitivity)

	script_findNext.canPropagate = True
	script_findNext.__doc__ = _(
		# Translators: documentation for script to manage headers
		"Goes to next result of current search"
	)

	def script_findPrevious(self, gesture):
		if not self._lastFindText:
			self.script_find(gesture, reverse=True)
			return
		self.searchFromItem = api.getFocusObject()
		self.doFindText(self._lastFindText, reverse=True, caseSensitive = self._lastCaseSensitivity)

	script_findPrevious.canPropagate = True
	script_findPrevious.__doc__ = _(
		# Translators: documentation for script to manage headers
		"Goes to previous result of current search"
	)

	def script_readListItems(self, gesture):
		curItem = api.getFocusObject()
		utils._RowsReader.readRows(curItem)

	script_readListItems.canPropagate = True
	script_readListItems.__doc__ = _(
		# Translators: documentation for script to read all list items starting from the focused one.
		"Starts reading all list items beginning at the item with focus"
	)

	@staticmethod
	def prepareForThreatedSearch():
		"""This method is executed before search is started in a separate thread.
		Base implementation does nothing.
		"""
		pass

	@staticmethod
	def threatedSearchDone():
		"""Executed when searching in a separate thread has been finished"""
		pass

	def isEmptyList(self):
		raise NotImplementedError

	def handleEmpty(self):
		if configManager.ConfigFromObject(self).announceEmptyLists:
			self.bindGesturesForEmpty()
			self.isEmpty = True

	def reportEmpty(self):
		# brailled and spoken the "0 items" message
		text = NVDALocale("%s items") % 0
		speech.speakMessage(text)
		region = braille.TextRegion(" {0}".format(text))
		region.focusToHardLeft = True
		region.update()
		braille.handler.buffer.regions.append(region)
		braille.handler.buffer.focus(region)
		braille.handler.buffer.update()
		braille.handler.update()

	def event_gainFocus(self):
		# call super to get list type/name reporting
		super(CRList, self).event_gainFocus()
		if self.supportsEmptyListAnnouncements and self.isEmptyList():
			self.handleEmpty()
		if hasattr(self, "isEmpty") and self.isEmpty:
			self.reportEmpty()

	def script_reportEmpty(self, gesture):
		if not self.isEmptyList():
			self.isEmpty = False
			self.bindCRGestures(reinitializeObj=True)
			return
		self.reportEmpty()

	def bindGesturesForEmpty(self):
		# bind arrows to focus again (and report empty)
		for item in ["Up", "Down", "Left", "Right"]:
			self.bindGesture("kb:{0}Arrow".format(item), "reportEmpty")
		# other useful gesture to remap
		scriptFuncs = (
			commands.script_reportCurrentFocus,
			commands.script_reportCurrentLine,
			commands.script_reportCurrentSelection
		)
		scriptDict = getScriptGestures(*scriptFuncs)
		for script, gestures in scriptDict.items():
			for gesture in gestures:
				self.bindGesture(gesture, "reportEmpty")

	def script_reportOrShowFormattingAtCaret(self, gesture):
		item = api.getFocusObject()
		dmti = DisplayModelTextInfo(item, textInfos.POSITION_ALL)
		# try to consider all object text chunks
		dmti.expand(textInfos.UNIT_LINE)
		fields = dmti.getTextWithFields()
		# collect all foreground and background colors
		fgColors = set()
		bgColors = set()
		for field in fields:
			if isinstance(field, textInfos.FieldCommand) and isinstance(field.field, textInfos.FormatField):
				fgColor = field.field.get("color")
				if fgColor: fgColors.add(fgColor.name)
				bgColor = field.field.get("background-color")
				if bgColor: bgColors.add(bgColor.name)
		if fgColors and bgColors:
			foregroundColors = ', '.join(fgColors)
			backgroundColors = ', '.join(bgColors)
			# Translators: message listing foreground over background colors
			message = _("{foregroundColors} over {backgroundColors}").format(foregroundColors=foregroundColors, backgroundColors=backgroundColors)
		else:
			message = NVDALocale("No formatting information")
		ui.message(message)
	script_reportOrShowFormattingAtCaret.canPropagate = True
	script_reportOrShowFormattingAtCaret.__doc__ = _(
		# Translators: Description of the keyboard command,
		# which reports foreground and background color of the current list item.
		"reports foreground and background colors of the current list item."
	)

class CRList32(CRList):
# for SysListView32 or WindowsForms10.SysListView32.app.0.*

	# flag to guarantee thread support
	THREAD_SUPPORTED = True
	supportsEmptyListAnnouncements = True

	def getColumnData(self, colNumber):
		curItem = api.getFocusObject()
		# even with no column, we consider
		# list item as placed in first column
		if (1 != colNumber > curItem.childCount) or (curItem.role == self.role):
			raise noColumnAtIndex
		if curItem.childCount:
			# for invisible column case
			num = self.getFixedNum(colNumber)
			# getChild is zero-based
			obj = curItem.getChild(num-1)
		else:
			obj = curItem
		# None obj should be generated
		# only in invisible column case
		if not obj:
			raise columnAtIndexNotVisible
		# generally, an empty name is a None object,
		# in Mozilla, instead, it's a unicode object with length 0
		if obj.name and len(obj.name):
			# obj.name is the column content
			content = obj.name
		else:
			content = None
		header = obj.columnHeaderText
		if not header or len(header) == 0:
			header = None
		return {"columnContent": content, "columnHeader": header}

	def getFixedNum(self, num):
		curItem = api.getFocusObject()
		child = curItem.simpleFirstChild
		startNum = child.columnNumber-1
		if num == 1:
			return startNum+1
		counter = 1
		stop = False
		while not stop:
			child = child.next
			if not child:
				break
			if states.INVISIBLE not in child.states:
				counter += 1
			if counter == num:
				stop = True
		return child.columnNumber if child else curItem.childCount+1

	def getHeaderParent(self):
		# faster than previous self.simpleParent.children[-1]
		headerHandle = watchdog.cancellableSendMessage(self.windowHandle, sysListView32.LVM_GETHEADER, 0, 0)
		headerParent = getNVDAObjectFromEvent(headerHandle, winUser.OBJID_CLIENT, 0)
		return headerParent

	def findInList(self, text, reverse, caseSensitive, stopCheck=lambda:False):
		"""performs search in item list, via object handles."""
		# specific implementation
		fg = api.getForegroundObject()
		listHandles = findAllDescendantWindows(fg.windowHandle, controlID=self.windowControlID)
		# if handle approach fails, use generic method
		if not listHandles:
			res = super(CRList32, self).findInList(text, reverse, caseSensitive)
			return res
		curItem = self.searchFromItem
		listLen = curItem.positionInfo["similarItemsInGroup"]
		# 1-based index
		curIndex = curItem.positionInfo["indexInGroup"]
		if reverse:
			indexes = rangeFunc(curIndex-1,0,-1)
		else:
			indexes = rangeFunc(curIndex+1,listLen+1)
		for index in indexes:
			item = getNVDAObjectFromEvent(self.windowHandle, winUser.OBJID_CLIENT, index)
			if not item or not item.name:
				continue
			if (
				(not caseSensitive and text.lower() in item.name.lower())
				or
				(caseSensitive and text in item.name)
			):
				return item
			if stopCheck():
				break

	def isMultipleSelectionSupported(self):
		try:
			curItem = self.searchFromItem
			states = curItem.IAccessibleObject.accState(curItem.IAccessibleChildID)
			if states & STATE_SYSTEM_MULTISELECTABLE:
				return True
		except:
			pass

	def successSearchAction(self, res):
		global useMultipleSelection
		speech.cancelSpeech()
		# reacquire res for this thread
		index = res.positionInfo["indexInGroup"]
		res = getNVDAObjectFromEvent(self.windowHandle, winUser.OBJID_CLIENT, index)
		if useMultipleSelection:
			res.IAccessibleObject.accSelect(SELFLAG_ADDSELECTION | SELFLAG_TAKEFOCUS, res.IAccessibleChildID)
		else:
		 res.IAccessibleObject.accSelect(SELFLAG_TAKESELECTION | SELFLAG_TAKEFOCUS, res.IAccessibleChildID)

	def getSelectedItems(self):
		parentHandle = self.windowHandle
		# index of first selected item
		# use -1 to query first list item too
		# with index 0L
		selItemIndex = watchdog.cancellableSendMessage(
			parentHandle,
			sysListView32.LVM_GETNEXTITEM,
			-1,
			ctypes.wintypes.LPARAM(sysListView32.LVNI_SELECTED)
		)
		listLen = watchdog.cancellableSendMessage(parentHandle, sysListView32.LVM_GETITEMCOUNT, 0, 0)
		items = []
		while (0 <= selItemIndex < listLen):
			item = getNVDAObjectFromEvent(parentHandle, winUser.OBJID_CLIENT, selItemIndex+1)
			itemChild = item.getChild(0)
			itemName = itemChild.name if itemChild else item.name
			if itemName:
				items.append(itemName)
			# index of next selected item
			selItemIndex = watchdog.cancellableSendMessage(
				parentHandle,
				sysListView32.LVM_GETNEXTITEM,
				selItemIndex,
				ctypes.wintypes.LPARAM(sysListView32.LVNI_SELECTED)
			)
		return items

	def isEmptyList(self):
		try:
			if self.childCount > 1:
				return False
			if (
				# simple and fast check
				(not self.rowCount)
				# usual condition for SysListView32
				# (the unique child should be the header list, that usually follows items)
				or (self.firstChild.role != roles.LISTITEM and self.firstChild == self.lastChild)
				# condition for possible strange cases
				or (self.childCount <= 1)
			):
				return True
			return False
		except AttributeError:
			return False


class CRList64(CRList):
	"""for 64-bit systems (DirectUIHWND window class)
	see CRList32 class for more comments
	"""

	THREAD_SUPPORTED = True
	# see reportEmptyFolder add-on
	supportsEmptyListAnnouncements = True

	# class-shared shell object
	shell = None
	# window shell variable
	curWindow = None

	def getColumnData(self, colNumber):
		# colNumber is passed as is, excluding the first position (0) of the children list
		# containing an icon, so this check in this way
		curItem = api.getFocusObject()
		if colNumber > curItem.childCount-1:
			raise noColumnAtIndex
		obj = curItem.getChild(colNumber)
		# obj.value is the column content
		# in Windows 7, an empty value is a None object,
		# in Windows 8, instead, it's a unicode object with length 0
		if obj and obj.value and len(obj.value):
			content = obj.value
		else:
			content = None
		# obj.name is the column header
		if obj and obj.name and len(obj.name):
			header = obj.name
		else:
			header = None
		return {"columnContent": content, "columnHeader": header}

	def getHeaderParent(self):
		# for imperscrutable reasons, this path gives the header container object
		# otherwise individually visible as first list children
		curItem = api.getFocusObject()
		headerParent = curItem.simpleParent.simpleFirstChild
		if headerParent.parent.role == roles.HEADER:
			return headerParent.parent
		else:
			return headerParent.next

	def preCheck(self, onFailureMsg=None):
		# create shared COM object if needed
		if not CRList64.shell:
			CRList64.shell = CreateObject("shell.application")
		# check to ensure shell32 method will work
		# (not available in all context, as open dialog)
		fg = api.getForegroundObject()
		for window in CRList64.shell.Windows():
			try:
				if window.hwnd and window.hwnd == fg.windowHandle:
					self.curWindow = window
					break
			except:
				pass
		if not self.curWindow:
			if onFailureMsg:
				ui.message(onFailureMsg)
			return False
		return True

	def getSelectedItems(self):
		# Translators: Reported when it is impossible to report currently selected items.
		if not self.preCheck(_("Current selection info not available")):
			return None
		items = [i.name for i in self.curWindow.Document.SelectedItems()]
		if items:
			# for some reasons, the last selected item appears as first, fix it
			lastItem = items.pop(0)
			items.append(lastItem)
		return items

	def script_find(self, gesture, reverse=False):
		# Translators: Reported when current list does not support searching.
		if self.preCheck(_("Cannot search here.")):
			super(CRList64, self).script_find(gesture, reverse)

	script_find.canPropagate = True
	script_find.__doc__ = CRList.script_find.__doc__

	def script_findNext(self, gesture):
		# Translators: Reported when current list does not support searching.
		if self.preCheck(_("Cannot search here.")):
			super(CRList64, self).script_findNext(gesture)
	script_findNext.canPropagate = True
	script_findNext.__doc__ = CRList.script_findNext.__doc__

	def script_findPrevious(self, gesture):
		# Translators: Reported when current list does not support searching.
		if self.preCheck(_("Cannot search here.")):
			super(CRList64, self).script_findPrevious(gesture)

	script_findPrevious.canPropagate = True
	script_findPrevious.__doc__ = CRList.script_findPrevious.__doc__

	def findInList(self, text, reverse, caseSensitive, stopCheck=lambda:False):
		"""performs search in item list, via shell32 object."""
		# reacquire curWindow for current thread
		self.preCheck()  # No message on failure here as we cannot hit this code path if shell is not supported.
		curFolder = self.curWindow.Document.Folder
		curItem = self.searchFromItem
		# names of children objects of current list item,
		# as "size", "modify date", "duration"...
		# note that icon has no name
		detailNames = [c.name for c in curItem.children if c.name]
		# corresponding indexes to query info for each file
		detailIndexes = []
		# 500 limit seems reasonable (they are 300+ on my system!)
		for index in rangeFunc(0,500):
			# localized detail name, as "size"
			detailName = curFolder.GetDetailsOf("", index)
			# we get index corresponding to name, so update lists
			if detailName in detailNames:
				detailNames.remove(detailName)
				detailIndexes.append(index)
			# to speed-up process, we want only visible details
			if not detailNames:
				break
		# useful to compute size
		bytePerSector = ctypes.c_ulonglong(0)
		# path without leading file://
		curPath = self.curWindow.LocationURL.rsplit("/", 1)[0][8:]
		# we get from current path, to ensure precision
		# also on external drives or different partitions (not verified)
		getBytePerSector(ctypes.c_wchar_p(curPath), None, ctypes.pointer(bytePerSector), None, None,)
		listLen = curItem.positionInfo["similarItemsInGroup"]
		# 1-based index
		curIndex = curItem.positionInfo["indexInGroup"]
		# pointer to item list
		items = curFolder.Items()
		resIndex = None
		if reverse:
#			indexes = rangeFunc(curIndex-2,-1,-1)
			# unfortunately, list pointer seems to change
			# for each query in reverse order
			# so, this range
			indexes = rangeFunc(0,curIndex-1)
		else:
			indexes = rangeFunc(curIndex,listLen)
		for index in indexes:
			# pointer to item
			item = items.Item(index)
			# detail value list
			tempItemInfo = []
			for detailIndex in detailIndexes:
				# getDetailsOf(item, 1) returns file size in KB, MB, etc,
				# item.size returns  as file size in bytes
				# but explorer shows file size on disk, in kilobytes...
				if (detailIndex == 1) and not item.IsFolder:
				# formula below is an optimization of ((item.size-1)/bytePerSector.value+1)*bytePerSector.value
					diskSizeB = ((item.size-1)&~(bytePerSector.value-1))+bytePerSector.value if item.size>512 else 1024
					diskSizeKB = int(round(diskSizeB/1024.0))
					# to insert thousands separator
					formattedSize = locale.format_string('%d', diskSizeKB, True)
					formattedSize = formattedSize if py3 else formattedSize.decode('mbcs')
					explorerSize = ' '.join([formattedSize, "KB"])
					tempItemInfo.append(explorerSize)
				else:
					tempItemInfo.append(curFolder.GetDetailsOf(item, detailIndex))
			# our reconstruction of item as shown in explorer
			itemInfo = '; '.join(tempItemInfo)
			# finally, the search if
			if (
				(not caseSensitive and text.lower() in itemInfo.lower())
				or
				(caseSensitive and text in itemInfo)
			):
				resIndex = index
				if not reverse:
					# we can stop; if reverse
					# we must scroll everything
					break
		return resIndex

	def isMultipleSelectionSupported(self):
		return True

	def successSearchAction(self, resIndex):
		global useMultipleSelection
		speech.cancelSpeech()
		# reacquire curWindow for current thread
		self.preCheck()  # No message on failure here as we cannot hit this code path if shell is not supported.
		# according to MS:
		# https://docs.microsoft.com/en-us/windows/desktop/shell/shellfolderview-selectitem
		# 17 should set focus and add item to selection,
		# 29 should set focus and exclusive selection
		if useMultipleSelection:
			resItem = self.curWindow.Document.Folder.Items().Item(resIndex)
			self.curWindow.Document.SelectItem(resItem, 17)
		else:
			resItem = self.curWindow.Document.Folder.Items().Item(resIndex)
			self.curWindow.Document.SelectItem(resItem, 29)

	@staticmethod
	def prepareForThreatedSearch():
		ctypes.windll.Ole32.CoInitialize(None)

	@staticmethod
	def threatedSearchDone():
		ctypes.windll.Ole32.CoUninitialize()

	def isEmptyList(self):
		# use UIA to avoid recursion error getting lastChild
		try:
			watchdog.alive()
#			childCount = watchdog.cancellableExecute(self._get_rowCount)
			childCount = self._get_UIAGridPattern().CurrentRowCount
		except:
			# assume not empty
			childCount = 1
		return not bool(childCount)

	def event_focusEntered(self):
		# to get "0 items" alert e.g. choosing
		# an empty folder in notepad open window
		super(CRList64, self).event_focusEntered()
		if hasattr(self, "isEmpty") and self.isEmpty:
			eventHandler.queueEvent("gainFocus", self)

	def event_gainFocus(self):
	# as in CRList, but without call to super
	# to avoid duplicate list type reporting
		if self.supportsEmptyListAnnouncements and self.isEmptyList():
			self.handleEmpty()
		if hasattr(self, "isEmpty") and self.isEmpty:
			self.reportEmpty()


class UIASuperGrid(CRList):

	# flag to guarantee thread support,
	# apparently, self-managed by UIAHandler.handler.MTAThreadFunc
	THREAD_SUPPORTED = True
	supportsEmptyListAnnouncements = True
	# available features from UIA
	UIAFeatures = None

	def preCheck(self, featureKeys, onFailureMsg=None):
		if self.UIAFeatures is None:
			# check and cache results
			self.UIAFeatures = {}.fromkeys(("selection","scroll","selectionItem", "grid"), False)
			if hasattr(self, 'UIASelectionPattern') and self.UIASelectionPattern is not None:
				self.UIAFeatures["selection"] = True
			# for some reason, NVDA does not expose UIAScrollPattern, so...
			if hasattr(self, '_getUIAPattern') and self._getUIAPattern(UIAHandler.UIA_ScrollPatternId, UIAHandler.IUIAutomationScrollPattern) is not None:
				self.UIAFeatures["scroll"] = True
			if hasattr(self, 'UIAGridPattern') and self.UIAGridPattern is not None:
				self.UIAFeatures["grid"] = True
		# check everytime
		focus = api.getFocusObject()
		if hasattr(focus, 'UIASelectionItemPattern') and focus.UIASelectionItemPattern is not None:
			self.UIAFeatures["selectionItem"] = True
		res = all((self.UIAFeatures[x] for x in featureKeys))
		if not res and onFailureMsg:
			ui.message(onFailureMsg)
		return res

	def getColumnData(self, colNumber):
		curItem = api.getFocusObject()
		if colNumber > curItem.childCount:
			raise noColumnAtIndex
		obj = curItem.getChild(colNumber-1)
		# obj.name is the column content
		if obj and obj.name and len(obj.name):
			content = obj.name
		else:
			content = None
		header = obj.columnHeaderText
		if not header or len(header) == 0:
			header = None
		return {"columnContent": content, "columnHeader": header}

	def script_manageHeaders(self, gesture):
		# no way to manage column headers at the moment;
		# investigating:
		# GetCurrentPropertyValue(UIAHandler.UIA_TableColumnHeadersPropertyId).QueryInterface(UIAHandler.IUIAutomationElementArray)
		ui.message(NVDALocale("Not supported in this document"))

	script_manageHeaders.canPropagate = True
	script_manageHeaders.__doc__ = CRList.script_manageHeaders.__doc__

	def getSelectedItems(self):
		# Translators: Reported when it is impossible to report currently selected items.
		if not self.preCheck(("selection",), _("Current selection info not available")):
			return None
		items = []
		try:
			selArray = self.UIASelectionPattern.GetCurrentSelection()
			for index in rangeFunc(0,selArray.Length):
				item = selArray.GetElement(index).CurrentName
				items.append(item)
		except AttributeError: # UIASelectionPattern absent or None
			pass
		return items

	def isMultipleSelectionSupported(self):
		# currently, scrolling the list brings to previous selection lost,
		# making this feature quite useless, so no support for now
		#try:
		#	return bool(self.UIASelectionPattern.CurrentCanSelectMultiple)
		#except AttributeError: # UIASelectionPattern absent or None
		return False

	def script_find(self, gesture, reverse=False):
		# Translators: Reported when current list does not support searching.
		if self.preCheck(("scroll", "selectionItem"), _("Cannot search here.")):
			super(UIASuperGrid, self).script_find(gesture, reverse)

	script_find.canPropagate = True
	script_find.__doc__ = CRList.script_find.__doc__

	def script_findNext(self, gesture):
		# Translators: Reported when current list does not support searching.
		if self.preCheck(("scroll", "selectionItem"), _("Cannot search here.")):
			super(UIASuperGrid, self).script_findNext(gesture)

	script_findNext.canPropagate = True
	script_findNext.__doc__ = CRList.script_findNext.__doc__

	def script_findPrevious(self, gesture):
		# Translators: Reported when current list does not support searching.
		if self.preCheck(("scroll", "selectionItem"), _("Cannot search here.")):
			super(UIASuperGrid, self).script_findPrevious(gesture)

	script_findPrevious.canPropagate = True
	script_findPrevious.__doc__ = CRList.script_findPrevious.__doc__

	def findInList(self, text, reverse, caseSensitive, stopCheck=lambda:False):
		# specific implementation
		curItem = self.searchFromItem
		curPos = curItem.positionInfo["indexInGroup"]
		listLen = curItem.positionInfo["similarItemsInGroup"]
		cl = UIAHandler.handler.clientObject
		classCond = cl.CreatePropertyCondition(UIAHandler.UIA_ClassNamePropertyId, "LeafRow")
		scrollManager = self._getUIAPattern(UIAHandler.UIA_ScrollPatternId, UIAHandler.IUIAutomationScrollPattern)
		verticalAmount = UIAHandler.ScrollAmount_LargeDecrement if reverse else UIAHandler.ScrollAmount_LargeIncrement
		while True:
			msgArr = self.UIAElement.FindAll(UIAHandler.TreeScope_Subtree, classCond)
			if reverse:
				indexes = rangeFunc(msgArr.Length-1, -1, -1)
			else:
				indexes = rangeFunc(0, msgArr.Length)
			for index in indexes:
				item = msgArr.GetElement(index)
				itemPos = item.GetCurrentPropertyValue(UIAHandler.UIA_PositionInSetPropertyId)
				if (reverse and itemPos >= curPos) or (not reverse and itemPos <= curPos):
					continue
				if (
					(not caseSensitive and text.lower() in item.CurrentName.lower())
					or
					(caseSensitive and text in item.CurrentName)
				):
					return item
			if stopCheck():
				break
			if (reverse and itemPos > 1) or (not reverse and itemPos < listLen):
				scrollManager.Scroll(UIAHandler.ScrollAmount_NoAmount, verticalAmount)
			else:
				return

	def successSearchAction(self, res):
		speech.cancelSpeech()
		selId = res.GetCurrentPattern(UIAHandler.UIA_SelectionItemPatternId)
		selManager = selId.QueryInterface(UIAHandler.IUIAutomationSelectionItemPattern)
		if useMultipleSelection:
			# when it'll be
			selManager.AddToSelection()
		else:
			selManager.Select()

	def isEmptyList(self):
		if self.preCheck(("grid",)):
			try:
				childCount = self.UIAGridPattern.CurrentRowCount
				return not bool(childCount)
			except:
				pass
		if self.childCount == 1 and self.firstChild.role == roles.PANE:
			# it's an empty list with header objs, so...
			return True
		else:
			return False


class MozillaTable(CRList32):
	"""Class to manage column headers in Mozilla list"""

	THREAD_SUPPORTED = True
	supportsEmptyListAnnouncements = True

	def _getColumnHeader(self, index):
		"""Returns the column header in Mozilla applications"""
		# get the list with headers, excluding these
		# which are not header (i.e. for settings, in Thunderbird)
		headers = [i for i in self.getHeaderParent().children if i.role == roles.TABLECOLUMNHEADER]
		# now, headers are not ordered as on screen,
		# but we deduce the order thanks to top location of each header
		headers.sort(key=lambda i: i.location)
		return headers[index-1].name

	def getFixedNum(self, num):
		return num

	def getHeaderParent(self):
		return self.simpleFirstChild

	def isMultipleSelectionSupported(self):
		return True

	def getSelectedItems(self):
		# specific implementation, see:
		# https://developer.mozilla.org.cach3.com/en-US/docs/Mozilla/Tech/XPCOM/Reference/Interface/IAccessibleTable2
		items = []
		table = self.IAccessibleTable2Object
		# workaround: selectedRows is broken in recent Thunderbird
		# use nColumns, nSelectedRows, selectedCells instead
		colNum = table.nColumns
		selRowNum = table.nSelectedRows
		selCellArray, selCellNum = table.selectedCells
		for row in rangeFunc(0, selRowNum):
			# to scan cells of the row
			rowRange = row*colNum
			itemCells = []
			for col in rangeFunc(0, colNum):
				if rowRange+col >= selCellNum:
					# it should not happen, but if it is,
					# subscripting cells crashes NVDA, so...
					continue
				try:
					cellText = selCellArray[rowRange+col].QueryInterface(IAccessible2).accName[0]
					if cellText:
						itemCells.append(cellText)
				except COMError: # unexplicable, but happens
					pass
			if itemCells:
				item = ' '.join(itemCells)+";"
			items.append(item)
		return items

	def script_reportCurrentSelection(self, gesture):
		# try to avoid COM call generates a crash
		if getLastScriptRepeatCount():
			sleep(0.5)
		super(MozillaTable, self).script_reportCurrentSelection(gesture)

	script_reportCurrentSelection.canPropagate = True
	script_reportCurrentSelection.__doc__ = CRList.script_reportCurrentSelection.__doc__

	def script_find(self, gesture, reverse=False):
		self.curPos = api.getFocusObject().IAccessibleObject.uniqueID
		super(MozillaTable, self).script_find(gesture, reverse)

	script_find.canPropagate = True
	script_find.__doc__ = CRList.script_find.__doc__

	def script_findNext(self, gesture):
		self.curPos = api.getFocusObject().IAccessibleObject.uniqueID
		super(MozillaTable, self).script_findNext(gesture)

	script_findNext.canPropagate = True
	script_findNext.__doc__ = CRList.script_findNext.__doc__

	def script_findPrevious(self, gesture):
		self.curPos = api.getFocusObject().IAccessibleObject.uniqueID
		super(MozillaTable, self).script_findPrevious(gesture)

	script_findPrevious.canPropagate = True
	script_findPrevious.__doc__ = CRList.script_findPrevious.__doc__

	def findInList(self, text, reverse, caseSensitive, stopCheck=lambda:False):
		"""performs the search in item list, via NVDA object navigation (MozillaTable specific)."""
		index = self.curPos
		curItem = getNVDAObjectFromEvent(self.windowHandle, winUser.OBJID_CLIENT, index)
		item = curItem.previous if reverse else curItem.next
		while (item and item.role == curItem.role):
			if (
				(not caseSensitive and item.name and text.lower() in item.name.lower())
				or
				(caseSensitive and text in item.name)
			):
				resIndex = item.IAccessibleObject.uniqueID
				return resIndex
			item = item.previous if reverse else item.next
			if stopCheck():
				break

	def successSearchAction(self, resIndex):
		global useMultipleSelection
		speech.cancelSpeech()
		# reacquire res for this thread
		res = getNVDAObjectFromEvent(self.windowHandle, winUser.OBJID_CLIENT, resIndex)
		# for some reasons, in Thunderbird xor of flagsSelect is not supported
		# so execute same actions but splitting calls
		if useMultipleSelection:
			res.IAccessibleObject.accSelect(SELFLAG_ADDSELECTION, res.IAccessibleChildID)
			res.IAccessibleObject.accSelect(SELFLAG_TAKEFOCUS, res.IAccessibleChildID)
		else:
		 res.IAccessibleObject.accSelect(SELFLAG_TAKESELECTION, res.IAccessibleChildID)
		 res.IAccessibleObject.accSelect(SELFLAG_TAKEFOCUS, res.IAccessibleChildID)

	def isEmptyList(self):
		try:
			if self.IAccessibleTable2Object.nRows == 0:
				return True
		except:
			pass
		return False


# Global ref on current finder
gFinder = None
# pref in find dialog
useMultipleSelection = False


class CRTreeview(CRList32):

	# flag to guarantee thread support
	THREAD_SUPPORTED = False
	supportsEmptyListAnnouncements = True

	def getColumnData(self, colNumber):
		curItem = api.getFocusObject()
		# header list to consider during handling
		headers = self.getHeaderParent().children
		# even with no column, we consider
		# list item as placed in first column
		if (1 != colNumber > len(headers)) or (curItem.role == self.role):
			raise noColumnAtIndex
		try:
			header = headers[colNumber-1].name
		except:
			header = None
		# too few cases, it's all a big try...
		try:
			if colNumber == 1:
				content = curItem.name
			else:
				if colNumber == len(headers):
					nextHeader = ""
				else:
					nextHeader = headers[colNumber].name
				content = curItem.description.split("%s: "%header, 1)[1].split(", %s: "%nextHeader, 1)[0]
		except:
			content = None
		return {"columnContent": content, "columnHeader": header}

	def getHeaderParent(self):
		return self.simplePrevious

	def findInList(self, text, reverse, caseSensitive, stopCheck=lambda:False):
		"""performs search in item list, via object handles."""
		# specific implementation
		fg = api.getForegroundObject()
		listHandles = findAllDescendantWindows(fg.windowHandle, controlID=self.windowControlID)
		# if handle approach fails, use generic method
		if not listHandles:
			# case not tested
			res = self.genericFindInList(text, reverse, caseSensitive)
			return res
		curItem = self.searchFromItem
		listLen = curItem.positionInfo["similarItemsInGroup"]
		# 1-based index
		curIndex = curItem.positionInfo["indexInGroup"]
		if reverse:
			indexes = rangeFunc(curIndex-1,0,-1)
		else:
			indexes = rangeFunc(curIndex+1,listLen+1)
		for index in indexes:
			item = getNVDAObjectFromEvent(self.windowHandle, winUser.OBJID_CLIENT, index)
			if not item or not item.name:
				continue
			if (
				(not caseSensitive and text.lower() in item.name.lower())
				or
				(not caseSensitive and text.lower() in item.description.lower())
				or
				(caseSensitive and text in item.name)
				or
				(caseSensitive and text in item.description)
			):
				return item
			if stopCheck():
				break

	def genericFindInList(self, text, reverse, caseSensitive, stopCheck=lambda:False):
		"""performs the search in treeview, via NVDA object navigation."""
		# generic implementation
		curItem = self.searchFromItem
		item = curItem.previous if reverse else curItem.next
		while (item and item.role == curItem.role):
			if (
				(not caseSensitive and item.name and text.lower() in item.name.lower())
				or
				(not caseSensitive and item.description and text.lower() in item.description.lower())
				or
				(caseSensitive and text in item.name)
				or
				(caseSensitive and text in item.description)
			):
				return item
			item = item.previous if reverse else item.next
			if stopCheck():
				break

	def successSearchAction(self, res):
		global useMultipleSelection
		speech.cancelSpeech()
		# reacquire res for this thread
		foundIndex = res.positionInfo["indexInGroup"]
		res = getNVDAObjectFromEvent(self.windowHandle, winUser.OBJID_CLIENT, foundIndex)
		resIndex = res.positionInfo["indexInGroup"]
		# sometime, due to list updates, items/indexes may differ
		if foundIndex != resIndex:
			res = getNVDAObjectFromEvent(self.windowHandle, winUser.OBJID_CLIENT, foundIndex+(foundIndex-resIndex))
		if useMultipleSelection:
			res.IAccessibleObject.accSelect(SELFLAG_ADDSELECTION | SELFLAG_TAKEFOCUS, res.IAccessibleChildID)
		else:
		 res.IAccessibleObject.accSelect(SELFLAG_TAKESELECTION | SELFLAG_TAKEFOCUS, res.IAccessibleChildID)

	def getSelectedItems(self):
		# generic (slow) implementation
		curItem = api.getFocusObject()
		items = []
		item = self.firstChild
		while (item and item.role == curItem.role):
			if states.SELECTED in item.states:
				itemName = ' '.join([item.name, item.description])
				if itemName:
					items.append(itemName)
			item = item.next
		return items

	def isEmptyList(self):
		try:
			childCount = self.childCount
		except:
			# assume not empty
			childCount = 1
		return not bool(childCount)


class Finder(Thread):

	STATUS_NOT_STARTED = 1
	STATUS_RUNNING = 2
	STATUS_COMPLETE = 3
	STATUS_ABORTED = 4

	def __init__(self, orig, text, reverse, caseSensitive, *args, **kwargs):
		super(Finder, self).__init__(*args, **kwargs)
		# renamed from _stop to _stopEvent, to avoid Py3 conflicts
		self._stopEvent = Event()
		self.orig = orig
		self.text = text
		self.reverse = reverse
		self.caseSensitive = caseSensitive
		self.res = None
		self.status = Finder.STATUS_NOT_STARTED

	def isAlive(self):
		if py3:
			# isAlive() is present, but deprecated
			return super(Finder, self).is_alive()
		else:
			return super(Finder, self).isAlive()

	def stop(self):
		self._stopEvent.set()
		self.status = Finder.STATUS_ABORTED

	def stopped(self):
		return self._stopEvent.is_set()

	def run(self):
		self.orig.prepareForThreatedSearch()
		self.status = Finder.STATUS_RUNNING
		self.res = self.orig.findInList(self.text, self.reverse, self.caseSensitive, self.stopped)
		if self.status == Finder.STATUS_RUNNING:
			self.status = Finder.STATUS_COMPLETE
		self.orig.threatedSearchDone()


class FindDialog(cursorManager.FindDialog):
	"""a class extending traditional find dialog."""

	def __init__(self, parent, cursorManager, *args):
		super(FindDialog, self).__init__(parent, cursorManager, *args)
		mainSizer = self.GetSizer()
		if not self.activeCursorManager.isMultipleSelectionSupported():
			return
		# Translators: Label of the checkbox in the find dialog which, if checked, selects multiple
		# items if they match the search query.
		self.multipleSelectionCheckBox = wx.CheckBox(self, wx.ID_ANY, label=_("Use multiple selection"))
		global useMultipleSelection
		self.multipleSelectionCheckBox.SetValue(useMultipleSelection)
		boxSizer = mainSizer.Children[0].Sizer
		pos = [c.Window for c in boxSizer.Children].index(self.caseSensitiveCheckBox) + 1
		boxSizer.Insert(pos, self.multipleSelectionCheckBox)
		boxSizer.InsertSpacer(pos, gui.guiHelper.SPACE_BETWEEN_VERTICAL_DIALOG_ITEMS)
		self.multipleSelectionCheckBox.MoveAfterInTabOrder(self.caseSensitiveCheckBox)
		self.Layout()
		mainSizer.Fit(self)
		self.CentreOnScreen()

	def onOk(self, evt):
		global useMultipleSelection
		if not self.activeCursorManager.isMultipleSelectionSupported():
			useMultipleSelection = False
		else:
			useMultipleSelection = self.multipleSelectionCheckBox.GetValue()
		super(FindDialog, self).onOk(evt)
