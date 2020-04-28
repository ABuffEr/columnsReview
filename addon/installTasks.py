import addonHandler
import os
import sys
py3 = sys.version.startswith("3")

addonHandler.initTranslation()

def onInstall():
	import gui
	import wx
	for addon in addonHandler.getAvailableAddons():
		if addon.name == "columnsReview":
			addonPath = addon.path if py3 else addon.path.encode("mbcs")
			iniFile = os.path.join(addonPath, "globalPlugins", "settings.ini")
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
