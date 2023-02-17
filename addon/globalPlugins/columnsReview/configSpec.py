# Config specification for the Columns Review add-on

try:
	from cStringIO import StringIO
except ModuleNotFoundError:  # Python 3
	from io import StringIO
from configobj import ConfigObj
from . actions import ACTIONS

configSpecString = ("""
[general]
	readHeader = boolean(default=True)
	copyHeader = boolean(default=True)
	announceEmptyList = boolean(default=True)
	announceListBounds = boolean(default=True)
[keyboard]
	useNumpadKeys = boolean(default=False)
	switchChar = string(default="-")
[gestures]
	NVDA = boolean(default=True)
	control = boolean(default=True)
	alt = boolean(default=False)
	shift = boolean(default=False)
	windows = boolean(default=False)
[actions]
	press1 = option({actionNames} default="read")
	press2 = option({actionNames} default="copy")
	press3 = option({actionNames} default="noAction")
	press4 = option({actionNames} default="noAction")
""".format(actionNames=''.join('"{}", '.format(action.name) for action in ACTIONS)[:-1]))
confspec = ConfigObj(StringIO(configSpecString), list_values=False, encoding="UTF-8")
confspec.newlines = "\r\n"
