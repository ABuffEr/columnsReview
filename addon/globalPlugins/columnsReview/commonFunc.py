# Utility functions for the Columns Review add-on

import ctypes
import winUser


# We need to store original NVDA gettext function,
# to be able to take advantage of messages translated in NVDA core.
NVDALocale = _

def rangeFunc(*args, **kwargs):
	try:
		import six
		return six.moves.range(*args, **kwargs)
	except ImportError:
		try:
			return __builtins__["xrange"](*args, **kwargs)
		except TypeError:
			return range(*args, **kwargs)

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


"""
to avoid code copying to exclude ui.message
This method is not used anywhere in the code - kept just for historical purposes.
def runSilently(func, *args, **kwargs):
	import speech
	import config
	configBackup = {"voice": speech.speechMode, "braille": config.conf["braille"]["messageTimeout"]}
	speech.speechMode = speech.speechMode_off
	config.conf["braille"]._cacheLeaf("messageTimeout", None, 0)
	try:
		func(*args, **kwargs)
	finally:
		speech.speechMode = configBackup["voice"]
		config.conf["braille"]._cacheLeaf("messageTimeout", None, configBackup["braille"])
"""


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
