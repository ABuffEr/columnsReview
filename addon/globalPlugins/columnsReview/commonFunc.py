# Utility functions for the Columns Review add-on

from .compat import CTWRAPPER
from NVDAObjects.IAccessible import getNVDAObjectFromEvent
from NVDAObjects.UIA import UIA
import ctypes
import winUser
import UIAHandler
import windowUtils

# We need to store original NVDA gettext function,
# to be able to take advantage of messages translated in NVDA core.
NVDALocale = _


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


# to get NVDA script gestures, regardless its user remap
def getScriptGestures(scriptFunc):
	from inputCore import manager
	allGestures = manager.getAllGestureMappings()
	scriptGestures = []
	try:
		scriptCategory = scriptFunc.category if hasattr(scriptFunc, "category") else scriptFunc.__self__.__class__.scriptCategory
		scriptDoc = scriptFunc.__doc__
		script = allGestures[scriptCategory][scriptDoc]
		scriptGestures = script.gestures
	except:
		pass
	# try to avoid garbageHandler warnings
	del allGestures
	return scriptGestures

def getFolderListViaUIA(startObj):
	cl = UIAHandler.handler.clientObject
	classCond = cl.CreatePropertyCondition(UIAHandler.UIA_ClassNamePropertyId, "UIItemsView")
	try:
		UIAPointer = startObj.UIAElement.FindFirstBuildCache(UIAHandler.TreeScope_Descendants, classCond, UIAHandler.handler.baseCacheRequest)
		folderList = UIA(UIAElement=UIAPointer)
	except:
		folderList = None
	return folderList

def getFolderListViaHandle(startObj):
	folderList = None
	cl = UIAHandler.handler.clientObject
	try:
		containerHandle = windowUtils.findDescendantWindow(startObj.windowHandle, visible=True, controlID=0, className="DirectUIHWND")
		containerObj = getNVDAObjectFromEvent(containerHandle, winUser.OBJID_CLIENT, 0)
		candidate = containerObj.simpleLastChild
		if candidate.role == CTWRAPPER.Role.LIST and hasattr(candidate, "UIAElement") and candidate.UIAElement.CurrentClassName == "UIItemsView":
			folderList = candidate
			# try to get UIA version
			UIAPointer = cl.elementFromHandleBuildCache(folderList.windowHandle, UIAHandler.handler.baseCacheRequest)
			folderList = UIA(UIAElement=UIAPointer)
	except:
		pass
	return folderList
