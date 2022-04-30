"""Provides various stuff used to preserve compatibility with older releases of NVDA."""

import controlTypes


class EnhancedGetter(object):

	def __init__(self, modWithAttrs, baseAttrName, gettersToTry):
		super(EnhancedGetter, self).__init__()
		self.mod = modWithAttrs
		self.baseAttrName = baseAttrName
		self.gettersToTry = gettersToTry

	def __getattr__(self, attrName):
		for possibleGetter in self.gettersToTry:
			try:
				return possibleGetter(self.mod, self.baseAttrName, attrName)
			except AttributeError:
				continue
		raise AttributeError("Attribute {} not found!".format(attrName))


class ControlTypesCompatWrapper(object):

	def __init__(self):
		super(ControlTypesCompatWrapper, self).__init__()
		self.Role = EnhancedGetter(
			controlTypes,
			"Role",
			[
				lambda mod, bName, name: getattr(mod, "{0}_{1}".format(bName.upper(), name)),
				lambda mod, bName, name: getattr(getattr(mod, bName), name),
			]
		)
		self.State = EnhancedGetter(
			controlTypes,
			"State",
			[
				lambda mod, bName, name: getattr(mod, "{0}_{1}".format(bName.upper(), name)),
				lambda mod, bName, name: getattr(getattr(mod, bName), name),
			]
		)


CTWRAPPER = ControlTypesCompatWrapper()


def rangeFunc(*args, **kwargs):
	try:
		import six
		return six.moves.range(*args, **kwargs)
	except ImportError:
		try:
			import __builtin__
			return __builtin__.xrange(*args, **kwargs)
		except ImportError:
			return range(*args, **kwargs)
