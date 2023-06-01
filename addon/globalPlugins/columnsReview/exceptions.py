# -*- coding: UTF-8 -*-
# Custom exceptions for the Columns Review add-on


class noColumnAtIndex(Exception):
	"""Raised when column at the specified index does not exist."""
	pass


class columnAtIndexNotVisible(Exception):
	"""Raised when column at the requested index exists, but is not visible."""
	pass
