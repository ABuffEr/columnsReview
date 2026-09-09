# -*- coding: UTF-8 -*-
# Provides various stuff used to preserve compatibility with older releases of NVDA.

import controlTypes

try:
	from braille.regions.base import TextRegion as TextRegion
except ImportError:
	# NVDA before 2027.1 exposes TextRegion directly in braille.
	from braille import TextRegion as TextRegion

try:
	from buildVersion import version_year, version_major, version_minor
except ImportError:
	from versionInfo import version_year, version_major, version_minor

currentVersion = (version_year, version_major, version_minor)

if currentVersion < (2024, 1, 0):
	zeroItemsTemplate = "%s items"
else:
	zeroItemsTemplate = ngettext("%s item", "%s items", 0)


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
			],
		)
		self.State = EnhancedGetter(
			controlTypes,
			"State",
			[
				lambda mod, bName, name: getattr(mod, "{0}_{1}".format(bName.upper(), name)),
				lambda mod, bName, name: getattr(getattr(mod, bName), name),
			],
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
