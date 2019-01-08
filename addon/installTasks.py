import addonHandler
import gui
import wx
import os

addonHandler.initTranslation()

def onInstall():
	for addon in addonHandler.getAvailableAddons():
		if addon.name == "columnsReview":
			iniFile = os.path.join(addon.path.decode("mbcs"), "globalPlugins", "settings.ini")
			if os.path.isfile(iniFile):
				gui.messageBox(
					# Translators: the label of a message box dialog.
					_("Previous add-on settings will be lost. Please configure it again, from NVDA preferences."),
					# Translators: the title of a message box dialog.
					_("Add-on settings reset"),
					wx.OK|wx.ICON_WARNING)
				try:
					os.remove(iniFile)
				except:
					pass
			break
