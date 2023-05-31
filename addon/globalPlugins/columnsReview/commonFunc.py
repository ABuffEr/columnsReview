# Utility functions for the Columns Review add-on

from .compat import CTWRAPPER
import ctypes
import winUser

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
def getScriptGestures(*args):
	from inputCore import manager
	allGestures = manager.getAllGestureMappings()
	scriptDict = {}
	for scriptFunc in args:
		scriptGestures = []
		try:
			scriptCategory = scriptFunc.category if hasattr(scriptFunc, "category") else scriptFunc.__self__.__class__.scriptCategory
			scriptDoc = scriptFunc.__doc__
			script = allGestures[scriptCategory][scriptDoc]
			scriptDict[scriptFunc] = script.gestures
		except:
			pass
	# try to avoid garbageHandler warnings
	del allGestures
	return scriptDict
