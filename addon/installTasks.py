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
		elif addon.name == "ExplorerEnhancements":
			if gui.messageBox(
				# Translators: the label of a message box dialog to uninstall another add-on
				_("You have installed {another_addon} by {another_author}, that causes problems with empty folder feature of ColumnsReview (if enabled); do you want to remove it now?").format(another_addon=addon.manifest["summary"], another_author=addon.manifest["author"]),
				# Translators: the title of a message box dialog.
				_("Warning!"),
				wx.YES|wx.NO|wx.ICON_WARNING) == wx.YES:
				addon.requestRemove()
