# Utility functions for the Columns Review add-on


def rangeFunc(*args, **kwargs):
	try:
		import six
		return six.moves.range(*args, **kwargs)
	except ImportError:
		try:
			return __builtins__["xrange"](*args, **kwargs)
		except TypeError:
			return range(*args, **kwargs)


# We need to store original NVDA gettext function,
# to be able to take advantage of messages translated in NVDA core.
NVDALocale = _
