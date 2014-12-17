# -*- coding: UTF-8 -*-
"""
@author: Alberto Buffolino
Last update: 13.12.2014
Code inspired by EnhancedListViewSupport plugin,
by Peter Vagner and contributors
"""
import addonHandler
import globalPluginHandler
import controlTypes
import api
import ui
from NVDAObjects.behaviors import RowWithFakeNavigation
import scriptHandler
import gui
import os
from configobj import *
import globalVars
import wx

addonHandler.initTranslation()

# load or create the .ini file
iniFile = os.path.join(os.path.dirname(__file__), "settings.ini").decode("mbcs")
myConf = ConfigObj(iniFile, encoding = "UTF8")
if not os.path.isfile(iniFile):
	myConf["general"] = {"readHeader": "True", "copyHeader": "True"}
	myConf["keyboard"] = {"useNumpadKeys": "False", "switchChar": "-"}
	myConf.write()
readHeader = bool(0 if myConf["general"]["readHeader"] == "False" else 1)
copyHeader = bool(0 if myConf["general"]["copyHeader"] == "False" else 1)
useNumpadKeys = bool(0 if myConf["keyboard"]["useNumpadKeys"] == "False" else 1)
switchChar = myConf["keyboard"]["switchChar"]

class ColumnsReview(RowWithFakeNavigation):
	"""the main abstract class that generates gestures
	and calculate index; subclasses must override it"""

	# set category
	_addonDir = os.path.join(os.path.dirname(__file__), "..").decode("mbcs")
	_curAddon = addonHandler.Addon(_addonDir)
	_addonSummary = _curAddon.manifest['summary']
	scriptCategory = unicode(_addonSummary)

	# the variable representing tens
	# of current interval (except the last column,
	# for which it's tens+1)
	tens = 0
	# the variable modulus useful in changeInterval script
	mod = 0
	# the variable which keeps track of the last chosen column number
	lastColumn = None

	def initOverlayClass(self):
		"""maps the correct gestures"""
		# obviously, empty lists are not handled
		if self.childCount < 0:
			return
		global useNumpadKeys, switchChar
		# a string useful for defining gestures
		nk = "numpad" if useNumpadKeys else ""
		# bind gestures from 1 to 9
		for n in xrange(1,10):
			self.bindGesture("kb:NVDA+control+%s%d" %(nk, n), "readColumn")
		if useNumpadKeys:
			# map numpadMinus for 10th column
			self.bindGesture("kb:NVDA+control+numpadMinus", "readColumn")
			# map numpadPlus to change interval
			self.bindGesture("kb:NVDA+control+numpadPlus", "changeInterval")
		else:
			# do same things for no numpad case
			self.bindGesture("kb:NVDA+control+0", "readColumn")
			self.bindGesture("kb:NVDA+control+%s" %switchChar, "changeInterval")

	#def script_readColumn(self,gesture):
		#raise NotImplementedError

	# Translators: documentation of script to read columns
	#script_readColumn.__doc__ = _("Returns the header and the content of the list column at the index corresponding to the number pressed")

	def getIndex(self, key):
		"""get index from key pressed"""
		# if key is not a digit
		# that is, "s" from numpadMinus
		if not key.isdigit():
			num = 0
		else:
			# get the digit pressed as index
			num = int(key)
		# if num == 0, from numpad or keyboard
		if num == 0:
			# set it to 10, 20, etc
			num = int(str(self.tens+1)+"0")
		else:
			# set it to 9, 13, 22, etc
			num = int(str(self.tens if self.tens != 0 else "")+str(num))
		return num

	def script_changeInterval(self, gesture):
		"""controls the grow of tens variable,
		it's built so to have always all gestures from 1 to 0"""
		# no further interval
		if self.childCount<10:
			# Translators: message when digit pressed exceed the columns number
			ui.message(_("No more columns available"))
			return
		# below operations are complicated to explain, so, for example:
		# in a list with 13 columns (childCount = 13), adding 9 to 13
		# we are sure that str(13+9)[:-1] return digits except last, that is,
		# the tens (or hundred and tens, etc) in max interval available
		# not considering the last column
		if not self.mod:
			#self.mod = int(str(self.childCount+9)[:-1])
			self.mod = self.childCount/10
		# now, we can scroll ten by ten among intervals, using modulus
		self.tens = (self.tens+1)%self.mod
		start = str(self.tens if self.tens != 0 else "")+"1"
		# nice: announce what is the absolutely last column available
		if self.tens == self.mod-1:
			end = str(self.childCount)
		else:
			# last column in interval has tens+1 as tens,
			# so "1"+"0" = "10" (string) in first interval
			# of our example
			end = str(self.tens+1)+"0"
		# Translators: message when you change interval in a list with more ten columns
		ui.message(_("From {start} to {end}").format(start=start, end=end))

	# Translators: documentation for script to change interval
	script_changeInterval.__doc__ = _("Cycles between a variable number of intervals of ten columns")

class ColumnsReview32(ColumnsReview):
# for SysListView32 or WindowsForms10.SysListView32.app.0.*

	def script_readColumn(self, gesture):
		"""main script to read columns"""
		# ask for index
		num = self.getIndex(gesture.mainKeyName[-1])
		if num > self.childCount:
			# Translators: message when digit pressed exceed the columns number
			ui.message(_("No more columns available"))
			return
		obj = self.getChild(num-1)
		# generally, an empty name is a None object,
		# in Mozilla, instead, it's a unicode object with length 0
		if obj is not None and obj.name is not None and len(obj.name) != 0:
			# obj.name is the column content
			content = unicode(obj.name+";")
		else:
			# Translators: message when cell in specified column is empty
			content = _("Not available;")
		global readHeader, copyHeader
		if scriptHandler.getLastScriptRepeatCount() != 0 and self.lastColumn == num:
			header = (unicode(self._getColumnHeader(num)+": ") if copyHeader else "")
			if api.copyToClip(header+content):
				# Translators: message announcing what was copied
				ui.message(_("Copied in clipboard: %s")%(header+content))
		else:
			header = (unicode(self._getColumnHeader(num)+": ") if readHeader else "")
			self.lastColumn = num
			ui.message(header+content)

class MozillaTable(ColumnsReview32):

	def _getColumnHeader(self, index):
		"""Returns the column header in Mozilla applications"""
		# get the list with headers, excluding last
		# that is not a header, but for settings
		headers = self.parent.firstChild.children[:-1]
		# now, headers is not ordered as on screen,
		# but we deduce the order thanks to top location of each header
		# so, first useful list
		origLocs = [x.location[0] for x in headers]
		# list with top locations ordered
		ordLocs = [x for x in origLocs]
		ordLocs.sort()
		# list with indexes of headers in real order
		ordIndexes = []
		for item in ordLocs:
			ordIndexes.append(origLocs.index(item))
		# finally, return the header
		return headers[ordIndexes[index-1]].name

class ColumnsReview64(ColumnsReview):
# for 64-bit systems (DirectUIHWND window class)
# see ColumnsReview32 class for more comments

	def script_readColumn(self,gesture):
		"""main script to read columns"""
		num = self.getIndex(gesture.mainKeyName[-1])
		# num is passed as is, excluding the first position (0) of the children list
		# containing an icon, so this check in this way
		if num > self.childCount-1:
			# Translators: message when digit pressed exceed the columns number
			ui.message(_("No more columns available"))
			return
		obj = self.getChild(num)
		# in Windows 7, an empty value is a None object,
		# in Windows 8, instead, it's a unicode object with length 0
		if obj is not None and obj.value is not None and len(obj.value) != 0:
			# obj.value is the column content
			content = unicode(obj.value+";")
		else:
			# Translators: message when cell in specified column is empty
			content = _("Not available;")
		global readHeader, copyHeader
		if scriptHandler.getLastScriptRepeatCount() != 0 and self.lastColumn == num:
			# obj.name is the column header
			header = (unicode(self.getChild(num).name+": ") if copyHeader else "")
			if api.copyToClip(header+content):
				# Translators: message announcing what was copied
				ui.message(_("Copied in clipboard: %s")%(header+content))
		else:
			header = (unicode(self.getChild(num).name+": ") if readHeader else "")
			self.lastColumn = num
			ui.message(header+content)

class ColumnsReviewSettingsDialog(gui.SettingsDialog):

	# Translators: title of settings dialog
	title = _("Columns Review Settings")

	def makeSettings(self, settingsSizer):
		global readHeader, copyHeader, useNumpadKeys, switchChar
		# Translators: label for first checkbox in settings
		self._readHeader = wx.CheckBox(self, label = _("Read the column header"))
		self._readHeader.SetValue(readHeader)
		settingsSizer.Add(self._readHeader)
		# Translators: label for 2nd checkbox in settings
		self._copyHeader = wx.CheckBox(self, label = _("Copy the column header"))
		self._copyHeader.SetValue(copyHeader)
		settingsSizer.Add(self._copyHeader)
		# Translators: label for 3rd checkbox in settings
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

	def postInit(self):
		self._readHeader.SetFocus()

	def onOk(self, evt):
		super(ColumnsReviewSettingsDialog, self).onOk(evt)
		# Update Configuration and global variables
		global readHeader, copyHeader, useNumpadKeys, switchChar
		readHeader = self._readHeader.IsChecked()
		myConf["general"]["readHeader"] = str(readHeader)
		copyHeader = self._copyHeader.IsChecked()
		myConf["general"]["copyHeader"] = str(copyHeader)
		useNumpadKeys = self._useNumpadKeys.IsChecked()
		myConf["keyboard"]["useNumpadKeys"] = str(useNumpadKeys)
		myConf["keyboard"]["switchChar"] = switchChar = self._switchChar.GetValue()
		myConf.write()

	def onCheck(self, evt):
		if self._useNumpadKeys.IsChecked():
			self.settingsSizer.Hide(self._switchCharLabel)
			self.settingsSizer.Hide(self._switchChar)
		else:
			self.settingsSizer.Show(self._switchCharLabel)
			self.settingsSizer.Show(self._switchChar)
		self.Fit()

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		if globalVars.appArgs.secure:
			return
		self.createMenu()

	def createMenu(self):
		self.prefsMenu = gui.mainFrame.sysTrayIcon.menu.GetMenuItems()[0].GetSubMenu()
		# Translators: menu item in preferences
		self.ColumnsReviewItem = self.prefsMenu.Append(wx.ID_ANY, _("Columns Review Settings..."), "")
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, lambda e: gui.mainFrame._popupSettingsDialog(ColumnsReviewSettingsDialog), self.ColumnsReviewItem)

	def terminate(self):
		try:
			self.prefsMenu.RemoveItem(self.ColumnsReviewItem)
		except wx.PyDeadObjectError:
			pass

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		if obj.role == controlTypes.ROLE_TABLEROW and obj.windowClassName == u'MozillaWindowClass':
			clsList.insert(0, MozillaTable)
		elif obj.role == controlTypes.ROLE_LISTITEM:
			if obj.windowClassName == "SysListView32" or u'WindowsForms10.SysListView32.app.0' in obj.windowClassName:
				clsList.insert(0, ColumnsReview32)
			elif obj.windowClassName == "DirectUIHWND":
				clsList.insert(0, ColumnsReview64)
