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

from .msg import message as NVDALocale
from NVDAObjects.IAccessible import getNVDAObjectFromEvent
from NVDAObjects.IAccessible.sysListView32 import * #List, ListItem, LVM_GETHEADER
from NVDAObjects.UIA import UIA # For UIA implementations only, chiefly 64-bit.
from NVDAObjects.behaviors import RowWithFakeNavigation
from appModules.explorer import GridTileElement, GridListTileElement # Specific for Start Screen tiles.
import sys
py3 = sys.version.startswith("3")
if py3:
	from io import StringIO
	from sayAllHandler import _activeSayAll, _ObjectsReader
	import weakref
	sayAllSuperclass = _ObjectsReader
else:
	from cStringIO import StringIO
	sayAllSuperclass = object
from comtypes.client import CreateObject
from comtypes.gen.IAccessible2Lib import IAccessible2
from configobj import *
from configobj import ConfigObj
from ctypes.wintypes import LPARAM as LParam
#from cursorManager import CursorManager
from globalCommands import commands
from gui.guiHelper import *
from logHandler import log
from oleacc import STATE_SYSTEM_MULTISELECTABLE, SELFLAG_TAKEFOCUS, SELFLAG_TAKESELECTION, SELFLAG_ADDSELECTION
from scriptHandler import isScriptWaiting, getLastScriptRepeatCount
from threading import Thread, Event
from time import sleep
from tones import beep
import addonHandler
import api
import braille
import config
import controlTypes as ct
import core
import ctypes
import cursorManager
import globalPluginHandler
import globalVars
import gui
import locale
import os
import speech
import ui
import watchdog
import winUser
import wx
try:
	from six.moves import range as rangeFunc
except ImportError:
	rangeFunc = xrange
except NameError:
	rangeFunc = range
from versionInfo import version_year, version_major
# useful to simulate profile switch handling
nvdaVersion = '.'.join([str(version_year), str(version_major)])
# rename for code clarity
SysLV32List = List
SysLV32Item = ListItem

addonDir = os.path.join(os.path.dirname(__file__), "..", "..")
if isinstance(addonDir, bytes):
	addonDir = addonDir.decode("mbcs")
curAddon = addonHandler.Addon(addonDir)
addonSummary = curAddon.manifest['summary']

addonHandler.initTranslation()

WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
def findAllDescendantWindows(parent, visible=None, controlID=None, className=None):
	"""See windowUtils.findDescendantWindow for parameters documentation."""
	results = []
	@WNDENUMPROC
	def callback(window, data):
		if (
			(visible is None or winUser.isWindowVisible(window) == visible)
			and (not controlID or winUser.getControlID(window) == controlID)
			and (not className or winUser.getClassName(window) == className)
		):
			results.append(window)
		return True
	# call previous func until it returns True,
	# thus always, getting all windows
	ctypes.windll.user32.EnumChildWindows(parent, callback, 0)
	# return all results
	return results

# to avoid code copying to exclude ui.message
def runSilently(func, *args, **kwargs):
	configBackup = {"voice": speech.speechMode, "braille": config.conf["braille"]["messageTimeout"]}
	speech.speechMode = speech.speechMode_off
	config.conf["braille"]._cacheLeaf("messageTimeout", None, 0)
	try:
		func(*args, **kwargs)
	finally:
		speech.speechMode = configBackup["voice"]
		config.conf["braille"]._cacheLeaf("messageTimeout", None, configBackup["braille"])

# to get NVDA script gestures, regardless its user remap
def getScriptGestures(scriptFunc):
	from inputCore import manager
	scriptGestures = []
	try:
		scriptCategory = scriptFunc.category if hasattr(scriptFunc, "category") else scriptFunc.__self__.__class__.scriptCategory
		scriptDoc = scriptFunc.__doc__
		scriptGestures = manager.getAllGestureMappings()[scriptCategory][scriptDoc].gestures
	except:
		pass
	return scriptGestures

def isEmptyList(lstObj):
	try:
		if (
				# simple and fast check
				(not lstObj.rowCount)
				or
				# usual condition for SysListView32
				# (the unique child should be the header list, that usually follows items)
				(lstObj.firstChild.role != ct.ROLE_LISTITEM and lstObj.firstChild == lstObj.lastChild)
				or
				# condition for possible strange cases
				(lstObj.childCount <= 1)
			):
				return True
		return False
	except:
		pass

# useful in ColumnsReview64 to calculate file size
getBytePerSector = ctypes.windll.kernel32.GetDiskFreeSpaceW

# init config
configSpecString = ("""
[general]
	readHeader = boolean(default=True)
	copyHeader = boolean(default=True)
	announceEmptyList = boolean(default=True)
[keyboard]
	useNumpadKeys = boolean(default=False)
	switchChar = string(default="-")
[gestures]
	NVDA = boolean(default=True)
	control = boolean(default=True)
	alt = boolean(default=False)
	shift = boolean(default=False)
	windows = boolean(default=False)
""")
confspec = ConfigObj(StringIO(configSpecString), list_values=False, encoding="UTF-8")
confspec.newlines = "\r\n"
config.conf.spec["columnsReview"] = confspec

# (re)load config
def loadConfig():
	global myConf, readHeader, copyHeader, announceEmptyList, useNumpadKeys, switchChar, baseKeys
	myConf = config.conf["columnsReview"]
	readHeader = myConf["general"]["readHeader"]
	copyHeader = myConf["general"]["copyHeader"]
	announceEmptyList = myConf["general"]["announceEmptyList"]
	useNumpadKeys = myConf["keyboard"]["useNumpadKeys"]
	switchChar = myConf["keyboard"]["switchChar"]
	configGestures = myConf["gestures"].items() if py3 else myConf["gestures"].iteritems()
	chosenKeys = [g[0] for g in configGestures if g[1]]
	baseKeys = '+'.join(chosenKeys)

class EmptyList(SysLV32List):
	"""Class to announce empty list."""

	def event_gainFocus(self):
		if not isEmptyList(self):
			self.clearGestureBindings()
			super(EmptyList, self).event_gainFocus()
			return
		super(EmptyList, self).event_gainFocus()
		# brailled and spoken the "0 elements" message
		text = ' '.join(["0", NVDALocale("Elements").lower()])
		speech.speakMessage(text)
		region = braille.TextRegion(" "+text)
		region.focusToHardLeft = True
		region.update()
		braille.handler.buffer.regions.append(region)
		braille.handler.buffer.focus(region)
		braille.handler.buffer.update()
		braille.handler.update()
		# bind arrows to focus again (and repeat message)
		for item in ["Up", "Down", "Left", "Right"]:
			self.bindGesture("kb:%sArrow"%item, "alert")
		# other useful gesture to remap
		# script_reportCurrentFocus
		for gesture in getScriptGestures(commands.script_reportCurrentFocus):
			self.bindGesture(gesture, "alert")
		# script_reportCurrentLine
		for gesture in getScriptGestures(commands.script_reportCurrentLine):
			self.bindGesture(gesture, "alert")
		# script_reportCurrentSelection
		for gesture in getScriptGestures(commands.script_reportCurrentSelection):
			self.bindGesture(gesture, "alert")

	def script_alert(self, gesture):
		self.event_gainFocus()

# Global ref on current finder
gFinder = None
# pref in find dialog
useMultipleSelection = False

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
		self.status = Finder.STATUS_RUNNING
		self.res = self.orig.findInList(self.text, self.reverse, self.caseSensitive, self.stopped)
		if self.status == Finder.STATUS_RUNNING:
			self.status = Finder.STATUS_COMPLETE

class ColumnsReview(RowWithFakeNavigation):
	"""The main abstract class that generates gestures and calculate index;
	classes that define new list types must override it,
	defining (or eventually re-defining) methods of this class."""

	scriptCategory = ' '.join([addonSummary, _("(DO NOT EDIT!)")])

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

	def initOverlayClass(self):
		"""maps the correct gestures"""
		# obviously, empty lists are not handled
		if self.childCount < 0:
			return
		global useNumpadKeys, switchChar, baseKeys
		# a string useful for defining gestures
		nk = "numpad" if useNumpadKeys else ""
		# bind gestures from 1 to 9
		for n in rangeFunc(1,10):
			self.bindGesture("kb:%s+%s%d"%(baseKeys, nk, n), "readColumn")
		if useNumpadKeys:
			# map numpadMinus for 10th column
			self.bindGesture("kb:%s+numpadMinus"%baseKeys, "readColumn")
			# ...numpadPlus to change interval
			self.bindGesture("kb:%s+numpadPlus"%baseKeys, "changeInterval")
			# delete for list item info
			self.bindGesture("kb:%s+numpadDelete"%baseKeys, "itemInfo")
			# ...and enter to headers manager
			self.bindGesture("kb:%s+numpadEnter"%baseKeys, "manageHeaders")
		else:
			# do same things for no numpad case
			self.bindGesture("kb:%s+0"%baseKeys, "readColumn")
			self.bindGesture("kb:%s+%s"%(baseKeys, switchChar), "changeInterval")
			self.bindGesture("kb:%s+delete"%baseKeys, "itemInfo")
			self.bindGesture("kb:%s+enter"%baseKeys, "manageHeaders")
		# find gestures
		self.bindGesture("kb:NVDA+control+f", "find")
		self.bindGesture("kb:NVDA+f3", "findNext")
		self.bindGesture("kb:NVDA+shift+f3", "findPrevious")
		# for current selection
		for gesture in getScriptGestures(commands.script_reportCurrentSelection):
			self.bindGesture(gesture, "reportCurrentSelection")
		# for say all
		# (available only after Py3 speech refactoring)
		if py3:
			for gesture in getScriptGestures(commands.script_sayAll):
				self.bindGesture(gesture, "sayAll")

	def script_readColumn(self,gesture):
		raise NotImplementedError

	# Translators: documentation of script to read columns
	script_readColumn.__doc__ = _("Returns the header and the content of the list column at the index corresponding to the number pressed")

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
		# no further interval
		if self.childCount<10:
			# Translators: message when digit pressed exceed the columns number
			ui.message(_("No more columns available"))
			return
		# in a list with 13 columns (childCount == 13),
		# childCount/10+1 (integer operation) gives all
		# intervals (2) of needed  10 columns;
		# if childCount is a multiple of 10 (es. 30),
		# we have exactly childCount/10=3 intervals.
		mod = self.childCount//10+(1 if self.childCount%10 else 0)
		# now, we can scroll ten by ten among intervals, using modulus
		self.tens = (self.tens+1)%mod
		# interval bounds to announce
		start = self.tens*10+1
		# nice: announce what is the absolutely last column available
		if self.tens == mod-1:
			end = self.childCount
		else:
			end = (self.tens+1)*10
		# Translators: message when you change interval in a list with more ten columns
		ui.message(_("From {start} to {end}").format(start=start, end=end))

	# Translators: documentation for script to change interval
	script_changeInterval.__doc__ = _("Cycles between a variable number of intervals of ten columns")

	def script_itemInfo(self, gesture):
		number = total = None
		try:
			number = self.positionInfo["indexInGroup"]
			total = self.positionInfo["similarItemsInGroup"]
		except:
			tempList = [i for i in self.parent.children if i.role == ct.ROLE_LISTITEM]
			if tempList:
				number = tempList.index(self)
				total = len(tempList)
		if None in (number, total):
			ui.message(_("No information available"))
		else:
			info = ' '.join([NVDALocale("item"), NVDALocale("{number} of {total}").format(number=number, total=total)])
			ui.message(info)

	# Translators: documentation for script to announce list item info
	script_itemInfo.__doc__ = _("Announces list item position information")

	def script_manageHeaders(self, gesture):
		def run():
			gui.mainFrame.prePopup()
			d = HeaderDialog(None, self.appModule.appName, self.getHeaderParent().children)
			if d:
				d.Show()
			gui.mainFrame.postPopup()
		wx.CallAfter(run)

	# Translators: documentation for script to manage headers
	script_manageHeaders.__doc__ = _("Provides a dialog for interactions with list column headers")

	def getHeaderParent(self):
		"""return the navigator object with header objects as children."""
		raise NotImplementedError

	def script_reportCurrentSelection(self, gesture):
		# generic (slow) implementation
		# (actually not used by any subclass)
		items = []
		item = self.parent.firstChild
		while (item and item.role == self.role):
			if ct.STATE_SELECTED in item.states:
				itemChild = item.getChild(0)
				itemName = itemChild.name if itemChild else item.name
				if itemName:
					items.append(itemName)
			item = item.next
		spokenItems = ', '.join(items)
		ui.message("%d %s: %s"%(len(items),
			# translators: message presented when get selected item count and names
			_("selected items"), spokenItems))

	# Translators: documentation for script to know current selected items
	script_reportCurrentSelection.__doc__ = _("Reports current selected list items")

	def script_find(self, gesture):
		if hasattr(cursorManager, "SEARCH_HISTORY_MOST_RECENT_INDEX"):
			d = FindDialog(gui.mainFrame, self, self._lastCaseSensitivity, self._searchEntries)
		else:
			d = FindDialog(gui.mainFrame, self, self._lastFindText, self._lastCaseSensitivity)
		gui.mainFrame.prePopup()
		d.Show()
		gui.mainFrame.postPopup()

	# Translators: documentation for script to find in list
	script_find.__doc__ = _("Provides a dialog for searching in item list")

	def doFindText(self, text, reverse=False, caseSensitive=False):
		"""manages actions pre and post search."""
		if not text:
			return
		speech.cancelSpeech()
		ui.message(_("Searching..."))
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
		ColumnsReview._lastFindText = text
		ColumnsReview._lastCaseSensitivity = caseSensitive

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
		# (actually not used by any subclass)
		item = self.previous if reverse else self.next
		while (item and item.role == self.role):
			if (
				(not caseSensitive and text.lower() in item.name.lower())
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
		# generic method
		# (actually not used by any subclass)
		speech.cancelSpeech()
		api.setNavigatorObject(res)
		runSilently(commands.script_navigatorObject_moveFocus, res)

	def script_findNext(self,gesture):
		if not self._lastFindText:
			self.script_find(gesture)
			return
		self.doFindText(self._lastFindText, caseSensitive = self._lastCaseSensitivity)

	# Translators: documentation for script to manage headers
	script_findNext.__doc__ = _("Goes to next result of current search")

	def script_findPrevious(self,gesture):
		if not self._lastFindText:
			self.script_find(gesture)
			return
		self.doFindText(self._lastFindText, reverse=True, caseSensitive = self._lastCaseSensitivity)

	# Translators: documentation for script to manage headers
	script_findPrevious.__doc__ = _("Goes to previous result of current search")

	def script_sayAll(self,gesture):
		readRows(self)

	# Translators: documentation for script to manage headers
	script_sayAll.__doc__ = _("Launches say all for next list items")

class FindDialog(cursorManager.FindDialog):
	"""a class extending traditional find dialog."""

	def __init__(self, parent, cursorManager, *args):
		super(FindDialog, self).__init__(parent, cursorManager, *args)
		mainSizer = self.GetSizer()
		if not self.activeCursorManager.isMultipleSelectionSupported():
			return
		self.multipleSelectionCheckBox = wx.CheckBox(self, wx.ID_ANY, label=_("Use multiple selection"))
		global useMultipleSelection
		self.multipleSelectionCheckBox.SetValue(useMultipleSelection)
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

def readRows(obj):
	global _activeSayAll
	reader = _RowsReader(obj)
	_activeSayAll = weakref.ref(reader)
	reader.next()

class _RowsReader(sayAllSuperclass):

	def walk(self, obj):
		yield obj
		nextObj = obj.next
		while nextObj:
			yield nextObj
			nextObj = nextObj.next

class ColumnsReview32(ColumnsReview):
# for SysListView32 or WindowsForms10.SysListView32.app.0.*

	# flag to guarantee thread support
	THREAD_SUPPORTED = True

	def script_readColumn(self, gesture):
		# ask for index
		num = self.getIndex(gesture.mainKeyName.rsplit('+', 1)[-1])
		if num > self.childCount:
			# Translators: message when digit pressed exceed the columns number
			ui.message(_("No more columns available"))
			return
		# for invisible column case
		num = self.getFixedNum(num)
		# getChild is zero-based
		obj = self.getChild(num-1)
		# None obj should be generated
		# only in invisible column case
		if not obj:
			# Translators: message when digit pressed not match a visible column
			ui.message(_("No more visible columns available"))
			return
		# generally, an empty name is a None object,
		# in Mozilla, instead, it's a unicode object with length 0
		if obj.name and len(obj.name):
			# obj.name is the column content
			content = ''.join([obj.name, ";"])
		else:
			# Translators: message when cell in specified column is empty
			content = _("Not available;")
		global readHeader, copyHeader
		if getLastScriptRepeatCount() and self.lastColumn == num:
			header = ''.join([obj.columnHeaderText, ": "]) if copyHeader else ""
			if api.copyToClip(header+content):
				# Translators: message announcing what was copied
				ui.message(_("Copied in clipboard: %s")%(header+content))
		else:
			header = ''.join([obj.columnHeaderText, ": "]) if readHeader else ""
			self.lastColumn = num
			ui.message(header+content)

	# Translators: documentation of script to read columns
	script_readColumn.__doc__ = _("Returns the header and the content of the list column at the index corresponding to the number pressed")

	def getFixedNum(self, num):
		child = self.simpleFirstChild
		startNum = child.columnNumber-1
		if num == 1:
			return startNum+1
		counter = 1
		stop = False
		while not stop:
			child = child.next
			if not child:
				break
			if ct.STATE_INVISIBLE not in child.states:
				counter += 1
			if counter == num:
				stop = True
		return child.columnNumber if child else self.childCount+1

	def getHeaderParent(self):
		# faster than previous self.simpleParent.children[-1]
		headerHandle = watchdog.cancellableSendMessage(self.simpleParent.windowHandle, LVM_GETHEADER, 0, 0)
		headerParent = getNVDAObjectFromEvent(headerHandle, winUser.OBJID_CLIENT, 0)
		return headerParent

	def findInList(self, text, reverse, caseSensitive, stopCheck=lambda:False):
		"""performs search in item list, via object handles."""
		# specific implementation
		fg = api.getForegroundObject()
		listHandles = findAllDescendantWindows(fg.windowHandle, controlID=self.windowControlID)
		thisList = None
		# there may be different lists with same controlID (see eMule)
		for handle in listHandles:
			tempList = getNVDAObjectFromEvent(handle, winUser.OBJID_CLIENT, 0)
			if tempList == self.simpleParent:
				thisList = tempList
				break
		# if handle approach fails, use generic method
		if not thisList:
			res = super(ColumnsReview32, self).findInList(text, reverse, caseSensitive)
			return res
		listLen = self.positionInfo["similarItemsInGroup"]
		# 1-based index
		curIndex = self.positionInfo["indexInGroup"]
		if reverse:
			indexes = rangeFunc(curIndex-1,0,-1)
		else:
			indexes = rangeFunc(curIndex+1,listLen+1)
		for index in indexes:
			item = getNVDAObjectFromEvent(thisList.windowHandle, winUser.OBJID_CLIENT, index)
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
			states = self.IAccessibleObject.accState(self.IAccessibleChildID)
			if states & STATE_SYSTEM_MULTISELECTABLE:
				return True
		except:
			pass

	def successSearchAction(self, res):
		speech.cancelSpeech()
		# for some reasons, in Thunderbird xor of flagsSelect is not supported
		# so execute same actions but splitting calls
		global useMultipleSelection
		if useMultipleSelection:
			res.IAccessibleObject.accSelect(SELFLAG_ADDSELECTION, res.IAccessibleChildID)
			res.IAccessibleObject.accSelect(SELFLAG_TAKEFOCUS, res.IAccessibleChildID)
		else:
		 res.IAccessibleObject.accSelect(SELFLAG_TAKESELECTION, res.IAccessibleChildID)
		 res.IAccessibleObject.accSelect(SELFLAG_TAKEFOCUS, res.IAccessibleChildID)

	def script_reportCurrentSelection(self, gesture):
		parentHandle = self.parent.windowHandle
		# index of first selected item
		# use -1 to query first list item too
		# with index 0L
		selItemIndex = watchdog.cancellableSendMessage(parentHandle, LVM_GETNEXTITEM, -1, LParam(LVNI_SELECTED))
		listLen = watchdog.cancellableSendMessage(parentHandle, LVM_GETITEMCOUNT, 0, 0)
		items = []
		while (0 <= selItemIndex < listLen):
			item = getNVDAObjectFromEvent(parentHandle, winUser.OBJID_CLIENT, selItemIndex+1)
			itemChild = item.getChild(0)
			itemName = itemChild.name if itemChild else item.name
			if itemName:
				items.append(itemName)
			# index of next selected item
			selItemIndex = watchdog.cancellableSendMessage(parentHandle, LVM_GETNEXTITEM, selItemIndex, LParam(LVNI_SELECTED))
		spokenItems = ', '.join(items)
		ui.message("%d %s: %s"%(len(items),
			# translators: message presented when get selected item count and names
			_("selected items"), spokenItems))

class MozillaTable(ColumnsReview32):
	"""Class to manage column headers in Mozilla list"""

	THREAD_SUPPORTED = False

	def _getColumnHeader(self, index):
		"""Returns the column header in Mozilla applications"""
		# get the list with headers, excluding these
		# which are not header (i.e. for settings, in Thunderbird)
		headers = [i for i in self.getHeaderParent().children if i.role == ct.ROLE_TABLECOLUMNHEADER]
		# now, headers are not ordered as on screen,
		# but we deduce the order thanks to top location of each header
		headers.sort(key=lambda i: i.location)
		return headers[index-1].name

	def getFixedNum(self, num):
		return num

	def getHeaderParent(self):
		# when thread view is disabled
		if self.role != ct.ROLE_TREEVIEWITEM:
			return self.simpleParent.simpleFirstChild
		# else, we manage the thread grouping case
		else:
			# tree-level of current obj
			level = self._get_IA2Attributes()["level"]
			# we go up level by level
			parent = self
			for n in rangeFunc(0,int(level)):
				parent = parent.simpleParent
			return parent.simpleFirstChild

	def script_reportCurrentSelection(self, gesture):
		# specific implementation, see:
		# https://developer.mozilla.org/en-US/docs/Mozilla/Tech/XPCOM/Reference/Interface/IAccessibleTable2
		# try to avoid COM call generates a crash
		if getLastScriptRepeatCount():
			sleep(0.5)
		table = self.parent.IAccessibleTable2Object
		selRowArray, selRowNum = table.selectedRows
		items = []
		colNum = table.nColumns
		for i in rangeFunc(0, selRowNum):
			row = selRowArray[i]
			itemCells = []
			for col in rangeFunc(0, colNum):
				cellText = table.cellAt(row, col).QueryInterface(IAccessible2).accName[0]
				itemCells.append(cellText)
			item = ' '.join(itemCells)
			items.append(item)
		spokenItems = ', '.join(items)
		ui.message("%d %s: %s"%(len(items),
			# translators: message presented when get selected item count and names
			_("selected items"), spokenItems))

	def isMultipleSelectionSupported(self):
		return True

	"""
	# old non-multiselection method, for reference
	def successSearchAction(self, res):
		speech.cancelSpeech()
		table = self.parent.IAccessibleTable2Object
		resIndex = res.positionInfo["indexInGroup"]-1
		table.selectRow(resIndex)
	"""

class ColumnsReview64(ColumnsReview):
	"""for 64-bit systems (DirectUIHWND window class)
	see ColumnsReview32 class for more comments"""

	THREAD_SUPPORTED = False

	# window shell variable
	curWindow = None

	def script_readColumn(self,gesture):
		num = self.getIndex(gesture.mainKeyName.rsplit('+', 1)[-1])
		# num is passed as is, excluding the first position (0) of the children list
		# containing an icon, so this check in this way
		if num > self.childCount-1:
			# Translators: message when digit pressed exceed the columns number
			ui.message(_("No more columns available"))
			return
		obj = self.getChild(num)
		# in Windows 7, an empty value is a None object,
		# in Windows 8, instead, it's a unicode object with length 0
		if obj and obj.value and len(obj.value):
			# obj.value is the column content
			content = ''.join([obj.value, ";"])
		else:
			# Translators: message when cell in specified column is empty
			content = _("Not available;")
		global readHeader, copyHeader
		if getLastScriptRepeatCount() and self.lastColumn == num:
			# obj.name is the column header
			header = ''.join([self.getChild(num).name, ": "]) if copyHeader else ""
			if api.copyToClip(header+content):
				# Translators: message announcing what was copied
				ui.message(_("Copied in clipboard: %s")%(header+content))
		else:
			header = ''.join([self.getChild(num).name, ": "]) if readHeader else ""
			self.lastColumn = num
			ui.message(header+content)

	# Translators: documentation of script to read columns
	script_readColumn.__doc__ = _("Returns the header and the content of the list column at the index corresponding to the number pressed")

	def getHeaderParent(self):
		# for imperscrutable reasons, this path gives the header container object
		# otherwise individually visible as first list children
		headerParent = self.simpleParent.simpleFirstChild
		if headerParent.parent.role == ct.ROLE_HEADER:
			return headerParent.parent
		else:
			return headerParent.next

	def preCheck(self):
		# check to ensure shell32 method will work
		# (not available in all context, as open dialog)
		shell = CreateObject("shell.application")
		fg = api.getForegroundObject()
		for window in shell.Windows():
			if window.hwnd == fg.windowHandle:
				self.curWindow = window
				break
		if not self.curWindow:
			ui.message(NVDALocale("Not supported in this document"))
			return False
		return True

	def script_reportCurrentSelection(self, gesture):
		if not self.preCheck():
			ui.message(_("Current selection info not available"))
			return
		items = [i.name for i in self.curWindow.Document.SelectedItems()]
		if items:
			# for some reasons, the last selected item appears as first, fix it
			lastItem = items.pop(0)
			items.append(lastItem)
		spokenItems = ', '.join(items)
		ui.message("%d %s: %s"%(len(items),
			# translators: message presented when get selected item count and names
			_("selected items"), spokenItems))

	def script_find(self, gesture):
		if self.preCheck():
			super(ColumnsReview64, self).script_find(gesture)

	def script_findNext(self, gesture):
		if self.preCheck():
			super(ColumnsReview64, self).script_findNext(gesture)

	def script_findPrevious(self, gesture):
		if self.preCheck():
			super(ColumnsReview64, self).script_findPrevious(gesture)

	def findInList(self, text, reverse, caseSensitive, stopCheck=lambda:False):
		"""performs search in item list, via shell32 object."""
		curFolder = self.curWindow.Document.Folder
		# names of children objects of current list item,
		# as "size", "modify date", "duration"...
		# note that icon has no name
		detailNames = [c.name for c in self.children if c.name]
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
		# also on external drives or different partitions
		getBytePerSector(ctypes.c_wchar_p(curPath), None, ctypes.pointer(bytePerSector), None, None,)
		listLen = self.positionInfo["similarItemsInGroup"]
		# 1-based index
		curIndex = self.positionInfo["indexInGroup"]
		# pointer to item list
		items = curFolder.Items()
		res = None
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
			for index in detailIndexes:
				# getDetailsOf(item, 1) returns file size in KB, MB, etc,
				# item.size returns  as file size in bytes
				# but explorer shows file size on disk, in kilobytes...
				if (index == 1) and not item.IsFolder:
				# formula below is an optimization of ((item.size-1)/bytePerSector.value+1)*bytePerSector.value
					diskSizeB = ((item.size-1)&~(bytePerSector.value-1))+bytePerSector.value if item.size>512 else 1024
					diskSizeKB = int(round(diskSizeB/1024.0))
					# to insert thousands separator
					formattedSize = locale.format_string('%d', diskSizeKB, True)
					formattedSize = formattedSize if py3 else formattedSize.decode('mbcs')
					explorerSize = ' '.join([formattedSize, "KB"])
					tempItemInfo.append(explorerSize)
				else:
					tempItemInfo.append(curFolder.GetDetailsOf(item, index))
			# our reconstruction of item as shown in explorer
			itemInfo = '; '.join(tempItemInfo)
			# finally, the search if
			if (
				(not caseSensitive and text.lower() in itemInfo.lower())
				or
				(caseSensitive and text in itemInfo)
			):
				res = item
				if not reverse:
					# we can stop; if reverse
					# we must scroll everything
					break
		return res

	def isMultipleSelectionSupported(self):
		return True

	def successSearchAction(self, res):
			speech.cancelSpeech()
			# according to MS:
			# https://docs.microsoft.com/en-us/windows/desktop/shell/shellfolderview-selectitem
			# 17 should set focus and add item to selection,
			# 29 should set focus and exclusive selection
			global useMultipleSelection
			if useMultipleSelection:
				self.curWindow.Document.SelectItem(res, 17)
			else:
				self.curWindow.Document.SelectItem(res, 29)

# for settings presentation compatibility
if hasattr(gui.settingsDialogs, "SettingsPanel"):
	superDialogClass = gui.settingsDialogs.SettingsPanel
else:
	superDialogClass = gui.SettingsDialog

class ColumnsReviewSettingsDialog(superDialogClass):
	"""Class to define settings dialog."""

	if hasattr(gui.settingsDialogs, "SettingsPanel"):
		# Translators: title of settings dialog
		title = _("Columns Review")
	else:
		# Translators: title of settings dialog
		title = _("Columns Review Settings")

	# common to dialog and panel
	def makeSettings(self, settingsSizer):
		global readHeader, copyHeader, useNumpadKeys, switchChar, announceEmptyList
		# Translators: label for read-header checkbox in settings
		self._readHeader = wx.CheckBox(self, label = _("Read the column header"))
		self._readHeader.SetValue(readHeader)
		settingsSizer.Add(self._readHeader)
		# Translators: label for copy-header checkbox in settings
		self._copyHeader = wx.CheckBox(self, label = _("Copy the column header"))
		self._copyHeader.SetValue(copyHeader)
		settingsSizer.Add(self._copyHeader)
		keysSizer = wx.StaticBoxSizer(wx.StaticBox(self,
			# Translators: Help message for sub-sizer of keys choices
			label=_("Choose the keys you want to use with numbers:")), wx.VERTICAL)
		self.keysChks = []
		configGestures = myConf["gestures"].items() if py3 else myConf["gestures"].iteritems()
		for keyName,keyEnabled in configGestures:
			chk = wx.CheckBox(self, label = NVDALocale(keyName))
			chk.SetValue(keyEnabled)
			keysSizer.Add(chk)
			self.keysChks.append((keyName, chk))
		settingsSizer.Add(keysSizer)
		# Translators: label for numpad keys checkbox in settings
		self._useNumpadKeys = wx.CheckBox(self, label = _("Use numpad keys to navigate through the columns"))
		self._useNumpadKeys.Bind(wx.EVT_CHECKBOX, self.onCheck)
		self._useNumpadKeys.SetValue(useNumpadKeys)
		settingsSizer.Add(self._useNumpadKeys)
		# Translators: label for edit field in settings, visible if previous checkbox is disabled
		self._switchCharLabel = wx.StaticText(self, label = _("Insert the char after \"0\" in your keyboard layout, or another char as you like:"))
		settingsSizer.Add(self._switchCharLabel)
		self._switchChar = wx.TextCtrl(self, name = "switchCharTextCtrl")
		self._switchChar.SetMaxLength(1)
		self._switchChar.SetValue(switchChar)
		settingsSizer.Add(self._switchChar)
		if self._useNumpadKeys.IsChecked():
			settingsSizer.Hide(self._switchCharLabel)
			settingsSizer.Hide(self._switchChar)
		# Translators: label for announce-empty-list checkbox in settings
		self._announceEmptyList = wx.CheckBox(self, label = _("Announce empty list"))
		self._announceEmptyList.SetValue(announceEmptyList)
		settingsSizer.Add(self._announceEmptyList)

	# for dialog only
	def postInit(self):
		self._readHeader.SetFocus()

	# shared between onOk and onSave
	def saveConfig(self):
		# Update Configuration
		myConf["general"]["readHeader"] = self._readHeader.IsChecked()
		myConf["general"]["copyHeader"] = self._copyHeader.IsChecked()
		myConf["general"]["announceEmptyList"] = self._announceEmptyList.IsChecked()
		for item in self.keysChks:
			myConf["gestures"][item[0]] = item[1].IsChecked()
		myConf["keyboard"]["useNumpadKeys"] = self._useNumpadKeys.IsChecked()
		myConf["keyboard"]["switchChar"] = self._switchChar.GetValue()
		# update global variables
		loadConfig()

	# for dialog only
	def onOk(self, evt):
		self.saveConfig()
		super(ColumnsReviewSettingsDialog, self).onOk(evt)

	# for panel only
	def onSave(self):
		self.saveConfig()

	def onCheck(self, evt):
		if self._useNumpadKeys.IsChecked():
			self.settingsSizer.Hide(self._switchCharLabel)
			self.settingsSizer.Hide(self._switchChar)
		else:
			self.settingsSizer.Show(self._switchCharLabel)
			self.settingsSizer.Show(self._switchChar)
		self.Fit()

class HeaderDialog(wx.Dialog):
	"""define dialog for column headers management."""

	def __init__(self, parent, appName, headerList):
		title = ' - '.join([_("Headers manager"), appName])
		super(HeaderDialog, self).__init__(parent, title=title)
		helperSizer = BoxSizerHelper(self, wx.HORIZONTAL)
		choices = [x.name if x.name else _("Unnamed header") for x in headerList]
		self.list = helperSizer.addLabeledControl(_("Headers:"), wx.ListBox, choices=choices)
		self.list.SetSelection(0)
		self.headerList = headerList
		actions = ButtonHelper(wx.VERTICAL)
		leftClickAction = actions.addButton(self, label=_("Left click"))
		leftClickAction.Bind(wx.EVT_BUTTON, self.onLeftClick)
		rightClickAction = actions.addButton(self, label=_("Right click"))
		rightClickAction.Bind(wx.EVT_BUTTON, self.onRightClick)
		helperSizer.addItem(actions)
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		mainSizer.Add(helperSizer.sizer, border=10, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		for item in [self.list, leftClickAction, rightClickAction]:
			item.Bind(wx.EVT_KEY_UP, self.onEscape)

	def onLeftClick(self, event):
		index = self.list.GetSelection()
		headerObj = self.headerList[index]
		self.Destroy()
		api.setNavigatorObject(headerObj)
		commands.script_moveMouseToNavigatorObject(None)
		winUser.mouse_event(winUser.MOUSEEVENTF_LEFTDOWN,0,0,None,None)
		winUser.mouse_event(winUser.MOUSEEVENTF_LEFTUP,0,0,None,None)
		ui.message(_("%s header clicked")%headerObj.name)

	def onRightClick(self, event):
		index = self.list.GetSelection()
		headerObj = self.headerList[index]
		self.Destroy()
		api.setNavigatorObject(headerObj)
		commands.script_moveMouseToNavigatorObject(None)
		winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTDOWN,0,0,None,None)
		winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTUP,0,0,None,None)
		ui.message(_("%s header clicked")%headerObj.name)

	def onEscape(self, event):
		if event.GetKeyCode() == wx.WXK_ESCAPE:
			self.Destroy()

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		if globalVars.appArgs.secure:
			return
		self.createMenu()
		if hasattr(config, "post_configProfileSwitch"):
			config.post_configProfileSwitch.register(self.handleConfigProfileSwitch)

	def createMenu(self):
		# Dialog or the panel.
		if hasattr(gui.settingsDialogs, "SettingsPanel"):
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(ColumnsReviewSettingsDialog)
		else:
			self.prefsMenu = gui.mainFrame.sysTrayIcon.menu.GetMenuItems()[0].GetSubMenu()
			# Translators: menu item in preferences
			self.ColumnsReviewItem = self.prefsMenu.Append(wx.ID_ANY, _("Columns Review Settings..."), "")
			gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, lambda e: gui.mainFrame._popupSettingsDialog(ColumnsReviewSettingsDialog), self.ColumnsReviewItem)

	def terminate(self):
		if hasattr(gui.settingsDialogs, "SettingsPanel"):
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(ColumnsReviewSettingsDialog)
		else:
			try:
				self.prefsMenu.RemoveItem(self.ColumnsReviewItem)
			except wx.PyDeadObjectError:
				pass

	def handleConfigProfileSwitch(self):
		loadConfig()

	def event_foreground(self, obj, nextHandler):
		if nvdaVersion < '2018.3':
			self.handleConfigProfileSwitch()
		nextHandler()

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		loadConfig()
		# to avoid crash in Win10 task manager
		if obj.role == ct.ROLE_LISTITEM and getattr(obj.appModule, "appName", None) == "taskmgr" and getattr(obj, "UIAElement", None):
			return
		if announceEmptyList and SysLV32List in clsList and obj.childCount <= 1:
			clsList.insert(0, EmptyList)
			return
#			elif obj.parent.windowClassName == "ListBox" and obj.role == ct.ROLE_UNKNOWN and not obj.name:
#				obj.name = NVDALocale("%s items")%0
		if obj.windowClassName == "MozillaWindowClass" and obj.role in (ct.ROLE_TABLEROW, ct.ROLE_TREEVIEWITEM):
			clsList.insert(0, MozillaTable)
		elif obj.role == ct.ROLE_LISTITEM:
			if SysLV32Item in clsList:
				clsList.insert(0, ColumnsReview32)
			elif UIA in clsList:
				# Windows 8/8.1/10 Start Screen tiles should not expose column info.
				if not obj.UIAElement.cachedClassName in ("GridTileElement", "GridListTileElement"):
					clsList.insert(0, ColumnsReview64)
#		elif obj.role == ct.ROLE_CHECKBOX and obj.windowClassName in [u'WuDuiListView', u'SysListView32']:
#			clsList.insert(0, CheckboxList)
