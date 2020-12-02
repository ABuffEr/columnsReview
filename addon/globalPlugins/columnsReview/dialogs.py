# GUI dialogs for the Columns Review add-on

import wx
import addonHandler
import config
import controlTypes as ct
import gui
from gui.guiHelper import BoxSizerHelper, ButtonHelper
import ui
import winUser
from .actions import ACTIONS, getActionIndexFromName
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

class HeaderDialog(wx.Dialog):
	"""define dialog for column headers management."""

	def __init__(self, title, headerList):
		super(HeaderDialog, self).__init__(None, title=' - '.join([_("Headers manager"), title]))
		helperSizer = BoxSizerHelper(self, wx.HORIZONTAL)
		visibleHeaders = [x for x in headerList if ct.STATE_INVISIBLE not in x.states]
		choices = [x.name if x.name else _("Unnamed header") for x in visibleHeaders]
		self.list = helperSizer.addLabeledControl(_("Headers:"), wx.ListBox, choices=choices)
		self.list.SetSelection(0)
		self.headerList = visibleHeaders
		actions = ButtonHelper(wx.VERTICAL)
		leftClickAction = actions.addButton(self, label=_("Left click"))
		leftClickAction.Bind(wx.EVT_BUTTON, lambda event: self.onButtonClick(event, "LEFT"))
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
		ui.message(_("%s header clicked") % headerObj.name)
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
