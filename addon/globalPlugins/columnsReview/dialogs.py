# GUI dialogs for the Columns Review add-on

import wx
import addonHandler
import config
import controlTypes as ct
import gui
from gui.guiHelper import BoxSizerHelper, ButtonHelper
import ui
import winUser


from .actions import ACTIONS, configuredActions, getActionIndexFromName
from .commonFunc import NVDALocale

addonHandler.initTranslation()


class configureActionPanel(wx.Panel):

	COPY_ACTION_INDEX = getActionIndexFromName("copy")
	READ_ACTION_INDEX = getActionIndexFromName("read")
	try:
		HIDE_NEXT_PANELS_AFTER = ACTIONS.index(
			[action for action in ACTIONS if action.showLaterActions is False][0]
		)
	except(IndexError, ValueError):
		HIDE_NEXT_PANELS_AFTER = None

	ON_PRESS_LABELS = {
		# Translators: Label of a combobox in which action can be assigned to a first press of the shortcut.
		1: _("On first press:"),
		# Translators: Label of a combobox in which action can be assigned to a second press of the shortcut.
		2: _("On second press:"),
		# Translators: Label of a combobox in which action can be assigned to a third press of the shortcut.
		3: _("On third press:"),
		# Translators: Label of a combobox in which action can be assigned to a fourth press of the shortcut.
		4: _("On fourth press:")
	}

	TRANSLATED_ACTION_NAMES = tuple(action.translatedName for action in ACTIONS)

	def __init__(self, parent, panelNumber, initialSelection):
		self.panelNumber = panelNumber
		super(configureActionPanel, self).__init__(parent)
		sizer = BoxSizerHelper(self, orientation=wx.VERTICAL)
		self.chooseActionCombo = sizer.addLabeledControl(
			self.ON_PRESS_LABELS[self.panelNumber],
			wx.Choice,
			choices=self.TRANSLATED_ACTION_NAMES
		)
		self.chooseActionCombo.SetSelection(initialSelection)
		self.chooseActionCombo.Bind(wx.EVT_CHOICE, self.onSelectedActionChange)
		# Translators: label for read-header checkbox in settings
		self.readHeader = wx.CheckBox(self, label=_("Read the column header"))
		self.readHeader.SetValue(config.conf["columnsReview"]["general"]["readHeader"])
		sizer.addItem(self.readHeader)
		# Translators: label for copy-header checkbox in settings
		self.copyHeader = wx.CheckBox(self, label=_("Copy the column header"))
		self.copyHeader.SetValue(config.conf["columnsReview"]["general"]["copyHeader"])
		sizer.addItem(self.copyHeader)
		self.setControlsVisibility()
		self.SetSizerAndFit(sizer.sizer)

	def onSelectedActionChange(self, evt):
		if evt.GetSelection() == self.READ_ACTION_INDEX and not self.Parent.readCheckboxEnabled:
			self.readHeader.Enable()
		else:
			self.readHeader.Disable()
		self.Parent.readCheckboxEnabled = any([p.readHeader.IsEnabled() for p in self.Parent.panels])
		if evt.GetSelection() == self.COPY_ACTION_INDEX and not self.Parent.copyCheckboxEnabled:
			self.copyHeader.Enable()
		else:
			self.copyHeader.Disable()
		self.Parent.copyCheckboxEnabled = any([p.copyHeader.IsEnabled() for p in self.Parent.panels])
		for panel in self.Parent.panels[self.panelNumber:]:
			panel.setControlsVisibility()
		if evt.GetSelection() == self.HIDE_NEXT_PANELS_AFTER:
			for panel in self.Parent.panels[self.panelNumber:]:
				panel.Disable()
		else:
			for panel in self.Parent.panels[self.panelNumber:]:
				panel.Enable()
				if panel.chooseActionCombo.GetSelection() == self.HIDE_NEXT_PANELS_AFTER:
					break
		self.Parent.settingsSizer.Fit(self.Parent)

	def setControlsVisibility(self):
		if self.chooseActionCombo.GetSelection() == self.READ_ACTION_INDEX and not self.Parent.readCheckboxEnabled:
			self.Parent.readCheckboxEnabled = True
			self.readHeader.Enable()
		else:
			self.readHeader.Disable()
		if self.chooseActionCombo.GetSelection() == self.COPY_ACTION_INDEX and not self.Parent.copyCheckboxEnabled:
			self.Parent.copyCheckboxEnabled = True
			self.copyHeader.Enable()
		else:
			self.copyHeader.Disable()


class ColumnsReviewSettingsDialog(getattr(gui.settingsDialogs, "SettingsPanel", gui.SettingsDialog)):
	"""Class to define settings dialog."""

	if hasattr(gui.settingsDialogs, "SettingsPanel"):
		# Translators: title of settings dialog
		title = _("Columns Review")
	else:
		# Translators: title of settings dialog
		title = _("Columns Review Settings")

	# common to dialog and panel
	def makeSettings(self, settingsSizer):
		self.copyCheckboxEnabled = self.readCheckboxEnabled = self.hideNextPanels = False
		self.panels = []
		panelsSizer = wx.StaticBoxSizer(
			wx.StaticBox(
				self,
				# Translators: Help message for group of comboboxes allowing to assign action to a keypress.
				label=_("When pressing combination to read column:")
			),
			wx.VERTICAL
		)
		for pressNumber, actionName in configuredActions().items():
			actionIndex = getActionIndexFromName(actionName)
			panel = configureActionPanel(self, pressNumber, actionIndex)
			panelsSizer.Add(panel)
			self.panels.append(panel)
			if self.hideNextPanels:
				panel.Disable()
			if panel.HIDE_NEXT_PANELS_AFTER is not None and actionIndex == panel.HIDE_NEXT_PANELS_AFTER:
				self.hideNextPanels = True
		settingsSizer.Add(panelsSizer)
		keysSizer = wx.StaticBoxSizer(
			wx.StaticBox(
				self,
				# Translators: Help message for sub-sizer of keys choices
				label=_("Choose the keys you want to use with numbers:")
			),
			wx.VERTICAL
		)
		self.keysChks = []
		gesturesSect = config.conf["columnsReview"]["gestures"]
		configGestures = gesturesSect.items() if hasattr(gesturesSect, "items") else gesturesSect.iteritems()
		for keyName, keyEnabled in configGestures:
			chk = wx.CheckBox(self, label=NVDALocale(keyName))
			chk.SetValue(keyEnabled)
			keysSizer.Add(chk)
			self.keysChks.append((keyName, chk))
		settingsSizer.Add(keysSizer)
		# Translators: label for numpad keys checkbox in settings
		self._useNumpadKeys = wx.CheckBox(self, label=_("Use numpad keys to navigate through the columns"))
		self._useNumpadKeys.Bind(wx.EVT_CHECKBOX, self.onCheck)
		self._useNumpadKeys.SetValue(config.conf["columnsReview"]["keyboard"]["useNumpadKeys"])
		settingsSizer.Add(self._useNumpadKeys)
		self._switchCharLabel = wx.StaticText(
			self,
			# Translators: label for edit field in settings, visible if previous checkbox is disabled
			label=_("Insert the char after \"0\" in your keyboard layout, or another char as you like:")
		)
		settingsSizer.Add(self._switchCharLabel)
		self._switchChar = wx.TextCtrl(self, name="switchCharTextCtrl")
		self._switchChar.SetMaxLength(1)
		self._switchChar.SetValue(config.conf["columnsReview"]["keyboard"]["switchChar"])
		settingsSizer.Add(self._switchChar)
		if self._useNumpadKeys.IsChecked():
			settingsSizer.Hide(self._switchCharLabel)
			settingsSizer.Hide(self._switchChar)
		self._announceEmptyList = wx.CheckBox(
			# Translators: label for announce-empty-list checkbox in settings
			self, label=_("Announce empty list (not working in Win8/10 folders")
		)
		self._announceEmptyList.SetValue(config.conf["columnsReview"]["general"]["announceEmptyList"])
		settingsSizer.Add(self._announceEmptyList)

	# for dialog only
	def postInit(self):
		for panel in self.panels:
			if panel.IsEnabled():
				panel.chooseActionCombo.SetFocus()
				break

	# shared between onOk and onSave
	def saveConfig(self):
		# Update Configuration
		copyChkFound = readChkFound = False
		actionsSection = config.conf["columnsReview"]["actions"]
		for panel in self.panels:
			if panel.IsEnabled():
				selectedActionName = ACTIONS[panel.chooseActionCombo.GetSelection()].name
				actionsSection["press{}".format(panel.panelNumber)] = selectedActionName
				if not readChkFound and panel.readHeader.IsEnabled():
					readChkFound = True
					config.conf["columnsReview"]["general"]["readHeader"] = panel.readHeader.IsChecked()
				if not copyChkFound and panel.copyHeader.IsEnabled():
					copyChkFound = True
					config.conf["columnsReview"]["general"]["copyHeader"] = panel.copyHeader.IsChecked()
			else:
				continue
		config.conf["columnsReview"]["general"]["announceEmptyList"] = self._announceEmptyList.IsChecked()
		for item in self.keysChks:
			config.conf["columnsReview"]["gestures"][item[0]] = item[1].IsChecked()
		config.conf["columnsReview"]["keyboard"]["useNumpadKeys"] = self._useNumpadKeys.IsChecked()
		config.conf["columnsReview"]["keyboard"]["switchChar"] = self._switchChar.GetValue()

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

	def __init__(self, title, headerList):
		# Translators: Title of the dialog which allows to perform actions on headers of the current list.
		super(HeaderDialog, self).__init__(None, title=' - '.join([_("Headers manager"), title]))
		helperSizer = BoxSizerHelper(self, wx.HORIZONTAL)
		visibleHeaders = [x for x in headerList if ct.STATE_INVISIBLE not in x.states]
		# Translators: Shown for a header which has no name.
		choices = [x.name if x.name else _("Unnamed header") for x in visibleHeaders]
		# Translators: Label for a list containing names of all headers of the current list.
		self.list = helperSizer.addLabeledControl(_("Headers:"), wx.ListBox, choices=choices)
		self.list.SetSelection(0 if len(choices) else -1)
		self.headerList = visibleHeaders
		actions = ButtonHelper(wx.VERTICAL)
		# Translators: Label for a button which clicks the given header with the left mouse button.
		leftClickAction = actions.addButton(self, label=_("Left click"))
		leftClickAction.Bind(wx.EVT_BUTTON, lambda event: self.onButtonClick(event, "LEFT"))
		# Translators: Label for a button which clicks the given header with the right mouse button.
		rightClickAction = actions.addButton(self, label=_("Right click"))
		rightClickAction.Bind(wx.EVT_BUTTON, lambda event: self.onButtonClick(event, "RIGHT"))
		helperSizer.addItem(actions)
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		mainSizer.Add(helperSizer.sizer, border=10, flag=wx.ALL)
		mainSizer.Fit(self)
		self.Bind(wx.EVT_CHAR_HOOK, self.onEscape)
		self.SetSizer(mainSizer)

	def onButtonClick(self, event, mouseButton):
		index = self.list.GetSelection()
		headerObj = self.headerList[index]
		self.Close()
		(left, top, width, height) = headerObj.location
		winUser.setCursorPos(left + (width // 2), top + (height // 2))
		winUser.mouse_event(getattr(winUser, "MOUSEEVENTF_{}DOWN".format(mouseButton)), 0, 0, None, None)
		winUser.mouse_event(getattr(winUser, "MOUSEEVENTF_{}UP".format(mouseButton)), 0, 0, None, None)
		# Translators: Announced when the given header has been clicked, 'headerName' is replaced with the name of
		# the  clicked object.
		ui.message(_("{headerName} header clicked").format(headerName=headerObj.name))
		self.Destroy()

	def onEscape(self, event):
		if event.GetKeyCode() == wx.WXK_ESCAPE:
			self.Destroy()
		else:
			event.Skip()

	@classmethod
	def Run(cls, title, headerList):
		gui.mainFrame.prePopup()
		d = cls(title, headerList)
		if d:
			d.Show()
		gui.mainFrame.postPopup()
