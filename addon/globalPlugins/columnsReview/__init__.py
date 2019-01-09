# -*- coding: UTF-8 -*-
# ColumnsReview
# A global plugin for NVDA
# Copyright 2014 Alberto Buffolino, released under GPL

# Add-on to manage columns in list views
# Code inspired by EnhancedListViewSupport plugin,
# by Peter Vagner and contributors

from logHandler import log
from .msg import message as NVDALocale
from cStringIO import StringIO
from comtypes.client import CreateObject
from configobj import ConfigObj
#from cursorManager import FindDialog
from NVDAObjects.IAccessible import getNVDAObjectFromEvent
from NVDAObjects.IAccessible.sysListView32 import List, ListItem
from NVDAObjects.UIA import UIA # For UIA implementations only, chiefly 64-bit.
from NVDAObjects.behaviors import RowWithFakeNavigation
from appModules.explorer import GridTileElement, GridListTileElement # Specific for Start Screen tiles.
from configobj import *
from globalCommands import commands
from gui.guiHelper import *
from scriptHandler import isScriptWaiting, getLastScriptRepeatCount
import addonHandler
import api
import braille
import config
import controlTypes as ct
import core
import cursorManager
import globalPluginHandler
import globalVars
import gui
import os
import speech
import ui
import winUser
import wx
try:
	from six.moves import range as rangeFunc
except ImportError:
	rangeFunc = xrange
except NameError:
	rangeFunc = range

addonHandler.initTranslation()

import ctypes
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
	chosenKeys = [g[0] for g in myConf["gestures"].iteritems() if g[1]]
	baseKeys = '+'.join(chosenKeys)

class EmptyList(List):
	"""Class to announce empty list."""

	def event_gainFocus(self):
		try:
			if (
				# usual condition for SysListView32
				# (the unique child should be the header list)
				(len(self.children) == 1 and not isinstance(self.children[0], ListItem))
				or
				# condition for possible strange cases
				(not len(self.children))
			):
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
					self.bindGesture("kb:%s" %item+"Arrow", "alert")
			else:
				self.clearGestureBindings()
				super(EmptyList, self).event_gainFocus()
		except:
			pass

	def script_alert(self, gesture):
		self.event_gainFocus()

class ColumnsReview(RowWithFakeNavigation):
	"""The main abstract class that generates gestures and calculate index;
	classes that define new list types must override it,
	defining (or eventually re-defining) methods of this class."""

	_lastFindText = ""
	_lastCaseSensitivity = False
	# the variable representing tens
	# of current interval (except the last column,
	# for which it's tens+1)
	tens = 0
	# the variable which keeps track of the last chosen column number
	lastColumn = None

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
			# ...and enter to headers manager
			self.bindGesture("kb:%s+numpadEnter"%baseKeys, "manageHeaders")
		else:
			# do same things for no numpad case
			self.bindGesture("kb:%s+0"%baseKeys, "readColumn")
			self.bindGesture("kb:%s+%s"%(baseKeys, switchChar), "changeInterval")
			self.bindGesture("kb:%s+enter"%baseKeys, "manageHeaders")
		self.bindGesture("kb:NVDA+control+f", "find")
		self.bindGesture("kb:NVDA+f3", "findNext")
		self.bindGesture("kb:NVDA+shift+f3", "findPrevious")

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
		mod = self.childCount/10+(1 if self.childCount%10 else 0)
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

	def script_manageHeaders(self, gesture):
		def run():
			gui.mainFrame.prePopup()
			d = HeadersDialog(None, self.appModule.appName, self.getHeadersParent().children)
			if d:
				d.Show()
			gui.mainFrame.postPopup()
		wx.CallAfter(run)

	# Translators: documentation for script to manage headers
	script_manageHeaders.__doc__ = _("Provides a dialog for interactions with list column headers")

	def getHeadersParent(self):
		"""return the navigator object with header objects as children."""
		raise NotImplementedError

	def script_find(self, gesture):
		d = FindDialog(gui.mainFrame, self, self._lastFindText, self._lastCaseSensitivity)
		gui.mainFrame.prePopup()
		d.Show()
		gui.mainFrame.postPopup()

	def getSubChildren(self, reverse, child, limit=100):
		childrenLen = self.positionInfo["similarItemsInGroup"]
		if childrenLen <= limit:
			items = self.simpleParent.children
			# 1-based index
			curIndex = self.positionInfo["indexInGroup"]
			if reverse:
				items = items[:curIndex-1]
				items.reverse()
			else:
				items = items[curIndex:]
			return (items, True)
		items = []
		finish = False
		newChild = child.previous if reverse else child.next
		count = 1
		while (newChild and count <= limit):
			items.append(newChild)
			count += 1
			newChild = newChild.previous if reverse else newChild.next
		if newChild is None:
			finish = True
		return (items, finish)

	def doFindText(self, text, reverse=False, caseSensitive=False):
		if not text:
			return
		res = None
		stop = False
		child = self
		while not(res or stop):
			items, stop = self.getSubChildren(reverse, child)
			for item in items:
				if (
					(item.name)
					and
					((text in item.name) if caseSensitive else (text.lower() in item.name.lower()))
				):
					res = item
					break
			if items:
				child = items[-1]
		if res:
			self.successSearchAction(res)
		else:
			wx.CallAfter(gui.messageBox, NVDALocale('text "%s" not found')%text, NVDALocale("Find Error"), wx.OK|wx.ICON_ERROR)
		ColumnsReview._lastFindText = text
		ColumnsReview._lastCaseSensitivity = caseSensitive

	def successSearchAction(self, res):
		speech.cancelSpeech()
		api.setNavigatorObject(res)
		runSilently(commands.script_navigatorObject_moveFocus, res)

	def script_findNext(self,gesture):
		if not self._lastFindText:
			self.script_find(gesture)
			return
		self.doFindText(self._lastFindText, caseSensitive = self._lastCaseSensitivity)

	def script_findPrevious(self,gesture):
		if not self._lastFindText:
			self.script_find(gesture)
			return
		self.doFindText(self._lastFindText, reverse=True, caseSensitive = self._lastCaseSensitivity)

class FindDialog(cursorManager.FindDialog):

	def onOk(self, evt):
		text = self.findTextField.GetValue()
		caseSensitive = self.caseSensitiveCheckBox.GetValue()
		# We must use core.callLater rather than wx.CallLater to ensure that the callback runs within NVDA's core pump.
		# If it didn't, and it directly or indirectly called wx.Yield, it could start executing NVDA's core pump from within the yield, causing recursion.
		core.callLater(300, self.activeCursorManager.doFindText, text, caseSensitive=caseSensitive)
		self.Destroy()

class ColumnsReview32(ColumnsReview):
# for SysListView32 or WindowsForms10.SysListView32.app.0.*

	def script_readColumn(self, gesture):
		# ask for index
		num = self.getIndex(gesture.mainKeyName.rsplit('+', 1)[-1])
		if num > self.childCount:
			# Translators: message when digit pressed exceed the columns number
			ui.message(_("No more columns available"))
			return
		obj = self.getChild(num-1)
		# generally, an empty name is a None object,
		# in Mozilla, instead, it's a unicode object with length 0
		if obj and obj.name and len(obj.name):
			# obj.name is the column content
			content = ''.join([obj.name, ";"])
		else:
			# Translators: message when cell in specified column is empty
			content = _("Not available;")
		global readHeader, copyHeader
		if getLastScriptRepeatCount() and self.lastColumn == num:
			header = ''.join([self._getColumnHeader(num), ": "]) if copyHeader else ""
			if api.copyToClip(header+content):
				# Translators: message announcing what was copied
				ui.message(_("Copied in clipboard: %s")%(header+content))
		else:
			header = ''.join([self._getColumnHeader(num), ": "]) if readHeader else ""
			self.lastColumn = num
			ui.message(header+content)

	# Translators: documentation of script to read columns
	script_readColumn.__doc__ = _("Returns the header and the content of the list column at the index corresponding to the number pressed")

	def getHeadersParent(self):
		return self.simpleParent.children[-1]

class MozillaTable(ColumnsReview32):
	"""Class to manage column headers in Mozilla list"""

	def _getColumnHeader(self, index):
		"""Returns the column header in Mozilla applications"""
		# get the list with headers, excluding these
		# which are not header (i.e. for settings, in Thunderbird)
		headers = [i for i in self.getHeadersParent().children if i.role == ct.ROLE_TABLECOLUMNHEADER]
		# now, headers are not ordered as on screen,
		# but we deduce the order thanks to top location of each header
		headers.sort(key=lambda i: i.location)
		return headers[index-1].name

	def getHeadersParent(self):
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

class ColumnsReview64(ColumnsReview):
	"""for 64-bit systems (DirectUIHWND window class)
	see ColumnsReview32 class for more comments"""

	def __init__(self, *args, **kwargs):
		super(ColumnsReview64, self).__init__(*args, **kwargs)
		folderDoc = None

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

	def getHeadersParent(self):
		return filter(lambda i: i.role == ct.ROLE_HEADER, self.simpleParent.children)[0]

	def getSubChildren(self, reverse, child, limit=None):
		items = []
		shell = CreateObject("shell.application")
		fg = api.getForegroundObject()
		for window in shell.Windows():
			if window.hwnd == fg.windowHandle:
				self.folderDoc = window.Document
		if not self.folderDoc:
				return (items, True)
		for item in self.folderDoc.Folder.Items():
			items.append(item)
		if items:
			if isinstance(child, self.__class__):
				# 1-based index
				curIndex = child.positionInfo["indexInGroup"]
			else:
				# zero-based index, +1 to normalize
				curIndex = items.index(child)+1
			if reverse:
				items = items[:curIndex-1]
				items.reverse()
			else:
				items = items[curIndex:]
		return (items, True)

	def successSearchAction(self, res):
			speech.cancelSpeech()
			self.folderDoc.SelectItem(res, 28)

#	script_find = script_findNext = script_findPrevious = (lambda self, gesture: ui.message("Operation not supported"))

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
		for keyName,keyEnabled in myConf["gestures"].iteritems():
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

class HeadersDialog(wx.Dialog):
	"""define dialog for column headers management."""

	def __init__(self, parent, appName, headersList):
		title = ' - '.join([_("Headers manager"), appName])
		super(HeadersDialog, self).__init__(parent, title=title)
		helperSizer = BoxSizerHelper(self, wx.HORIZONTAL)
		choices = [x.name if x.name else _("Unnamed header") for x in headersList]
		self.list = helperSizer.addLabeledControl(_("Headers:"), wx.ListBox, choices=choices)
		self.list.SetSelection(0)
		self.headersList = headersList
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
		headerObj = self.headersList[index]
		self.Destroy()
		api.setNavigatorObject(headerObj)
		commands.script_moveMouseToNavigatorObject(None)
		winUser.mouse_event(winUser.MOUSEEVENTF_LEFTDOWN,0,0,None,None)
		winUser.mouse_event(winUser.MOUSEEVENTF_LEFTUP,0,0,None,None)
		ui.message(_("%s header clicked")%headerObj.name)

	def onRightClick(self, event):
		index = self.list.GetSelection()
		headerObj = self.headersList[index]
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

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		loadConfig()
		if announceEmptyList and obj.role == ct.ROLE_LIST and "listview" in obj.windowClassName.lower():
			clsList.insert(0, EmptyList)
		if obj.windowClassName == 'MozillaWindowClass' and obj.role in [ct.ROLE_TABLEROW, ct.ROLE_TREEVIEWITEM]:
			clsList.insert(0, MozillaTable)
		elif obj.role == ct.ROLE_LISTITEM:
			if obj.windowClassName == "SysListView32" or 'WindowsForms10.SysListView32.' in obj.windowClassName:
				clsList.insert(0, ColumnsReview32)
			elif obj.windowClassName == "DirectUIHWND" and isinstance(obj, UIA):
				# Windows 8/8.1/10 Start Screen tiles should not expose column info.
				if not obj.UIAElement.cachedClassName in ("GridTileElement", "GridListTileElement"):
					clsList.insert(0, ColumnsReview64)
#		elif obj.role == ct.ROLE_CHECKBOX and obj.windowClassName in [u'WuDuiListView', u'SysListView32']:
#			clsList.insert(0, CheckboxList)
