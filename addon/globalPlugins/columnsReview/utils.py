# -*- coding: UTF-8 -*-
# Utility classes for the Columns Review add-on


def getRowsReaderSuperClass():
	"""Depending on the version of NVDA in use say all for list items is
	either not supported at all (pre 2019.3 / speech refactor) or the base class allowing for reading objects
	is defined in a different places."""
	try:
		import sayAllHandler as SAH
	except ImportError:
		import speech.sayAll as SAH
	return getattr(SAH, "_ObjectsReader", object)


class _RowsReader(getRowsReaderSuperClass()):

	def walk(self, obj):
		yield obj
		nextObj = obj.next
		while nextObj:
			yield nextObj
			nextObj = nextObj.next

	@classmethod
	def readRows(cls, obj):
		import weakref
		try:
			import sayAllHandler
			reader = cls(obj)
			sayAllHandler._activeSayAll = weakref.ref(reader)
		except ImportError:
			import speech.sayAll
			reader = cls(speech.sayAll.SayAllHandler, obj)
			speech.sayAll.SayAllHandler._getActiveSayAll = weakref.ref(reader)
		reader.next()

	@classmethod
	def isSupported(cls):
		"""While relying on the MRO of the class is a bit tricky it avoids a lot of code duplication"""
		return len(cls.__mro__) > 2  # The clas itself  and object- if MRO is longer super class exists.
