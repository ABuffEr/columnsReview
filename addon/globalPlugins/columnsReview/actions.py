# Defines actions for the columns Review add-on

import addonHandler
import api
import config
import speech
import ui

from .commonFunc import rangeFunc

addonHandler.initTranslation()


class Action(object):
	"""Represents an action executed in response to a key press.
	Objects inheriting from this class can be used as a callable which accepts two params:
	column content and column header.
	"""

	name = ""  # Internal name of this action.
	translatedName = ""  # Description of this action shown to the user in settings dialog.
	performsAction = False  # Set to True if the given object does something when called.
	# Set to False if actions assigned to the later key presses
	# should be  hidden in the settings dialog - useful if the given action moves focus somewhere.
	showLaterActions = True

	def __call__(self, content, header):
		raise NotImplementedError


class NoAction(Action):
	"""Dummy action assigned to key presses which shouldn't do anything"""

	name = "noAction"
	# Translators: Description of the action which simply ignores the pressed key
	translatedName = _("Do nothing")


class ReadAction(Action):
	"""Read content, and optionally header, of the given column."""

	name = "read"
	# Translators: Name of the action which reads given column.
	translatedName = _("Read column")
	performsAction = True

	def __call__(self, columnContent, columnHeader):
		if not columnContent:
			# Translators: Presented for an empty column.
			columnContent = _("Empty column")
		if not columnHeader or config.conf["columnsReview"]["general"]["readHeader"] is False:
			columnHeader = ""
		else:
			columnHeader = u"{}: ".format(columnHeader)
		ui.message(u"{0}{1}".format(columnHeader, columnContent))


class CopyAction(Action):
	"""Copies content, and optionally header, of the given column."""

	name = "copy"
	# Translators: Name of the action which copies given column.
	translatedName = _("Copy column")
	performsAction = True

	def __call__(self, columnContent, columnHeader):
		if not columnContent:
			# Translators: Presented for an empty column.
			columnContent = _("Empty column")
		if not columnHeader or config.conf["columnsReview"]["general"]["copyHeader"] is False:
			columnHeader = ""
		else:
			columnHeader = u"{}: ".format(columnHeader)
		res = u"{0}{1}".format(columnHeader, columnContent)
		if api.copyToClip(res):
			# Translators: message announcing what was copied
			ui.message(u"{} copied.".format(res))


class SpellAction(Action):
	"""Spells content of the given column."""

	name = "spell"
	# Translators: Name of the action which spells given column.
	translatedName = _("Spell column")
	performsAction = True

	def __call__(self, columnContent, columnHeader):
		if not columnContent:
			# Translators: Presented for an empty column.
			ui.message(_("Empty column"))
			return
		speech.speakSpelling(columnContent)


class DisplayAction(Action):
	"""Displays content of the given column in the browseable message"""

	name = "display"
	# Translators: Name of the action which displays content of the given column in the browseable message.
	translatedName = _("Show column content in browse mode")
	performsAction = True
	showLaterActions = False  # The list item with focus loses it when browseable message is shown.

	def __call__(self, columnContent, columnHeader):
		if not columnContent:
			# Translators: Presented for an empty column.
			ui.message(_("Empty column"))
			return
		if not columnHeader:
			columnHeader = u""
		ui.browseableMessage(columnContent, title=columnHeader)


# List of actions in order in which they appear in the  GUI
# when implementing a new one please add it at the end.
ACTIONS = (
	NoAction(),
	ReadAction(),
	CopyAction(),
	SpellAction(),
	DisplayAction()
)


def actionFromName(name):
	matchingActions = [action for action in ACTIONS if action.name == name]
	if not matchingActions:
		raise RuntimeError("Action named %s  does not exist" % (name))
	if len(matchingActions) > 1:
		raise RuntimeError(
			"More than one action with such name exist."
			"This is unexpected."
		)
	return matchingActions[0]


def getActionIndexFromName(name):
	for actionIndex, actionObject in enumerate(ACTIONS):
		if actionObject.name == name:
			return actionIndex
	raise ValueError("Action named %s not in actions list" % name)


def configuredActions():
	pressesToActions = dict()
	actionsSection = config.conf["columnsReview"]["actions"]
	for num in rangeFunc(1, len(ACTIONS)):
		pressesToActions[num] = actionsSection["press{}".format(num)]
	return pressesToActions
