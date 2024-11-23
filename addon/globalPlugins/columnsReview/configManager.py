# -*- coding: UTF-8 -*-
import config
try:
	from configobj.validate import is_boolean
except ImportError:
	from validate import is_boolean


class ConfigFromObject(object):

	def __init__(self, obj):
		self.obj = obj
		try:
			self.possibleTriggerName = "app:{0}".format(self.obj.appModule.appName)
		except AttributeError:
			self.possibleTriggerName = None

	@property
	def triggersApplyForObj(self):
		return (
			list(config.conf.listProfiles())
			and config.conf.profileTriggersEnabled
			and not config.conf._suspendedTriggers
			and self.possibleTriggerName is not None
			and self.possibleTriggerName in config.conf.triggersToProfiles.keys()
		)

	def getApplicableProfiles(self):
		if self.triggersApplyForObj:
			res = []
			if len(config.conf.profiles) > 1:
				profileName = config.conf.profiles[-1].name
				# avoid occasional no manual AttributeError
				# maybe due to cache updating
				if getattr(config.conf._profileCache[profileName], "manual", False):
					res.append(config.conf._profileCache[config.conf.profiles[-1].name])
			try:
				res.append(config.conf._profileCache[config.conf.triggersToProfiles[self.possibleTriggerName]])
			except KeyError:
				try:
					config.conf._getProfile(config.conf.triggersToProfiles[self.possibleTriggerName])
					res.append(config.conf._profileCache[config.conf.triggersToProfiles[self.possibleTriggerName]])
				except KeyError:
					pass
			res.append(config.conf._profileCache[None])  # Default config
			res.append(config.conf)
		else:
			res = [config.conf]
		return res

	@property
	def announceEmptyLists(self):
		for profile in self.getApplicableProfiles():
			try:
				return is_boolean(profile["columnsReview"]["general"]["announceEmptyList"])
			except KeyError:
				continue

	@property
	def announceListBounds(self):
		for profile in self.getApplicableProfiles():
			try:
				return is_boolean(profile["columnsReview"]["general"]["announceListBounds"])
			except KeyError:
				continue

	@property
	def announceListBoundsWith(self):
		for profile in self.getApplicableProfiles():
			try:
				return profile["columnsReview"]["general"]["announceListBoundsWith"]
			except KeyError:
				continue

	@property
	def topBeep(self):
		for profile in self.getApplicableProfiles():
			try:
				return int(profile["columnsReview"]["beep"]["topBeep"])
			except KeyError:
				continue

	@property
	def bottomBeep(self):
		for profile in self.getApplicableProfiles():
			try:
				return int(profile["columnsReview"]["beep"]["bottomBeep"])
			except KeyError:
				continue

	@property
	def beepLen(self):
		for profile in self.getApplicableProfiles():
			try:
				return int(profile["columnsReview"]["beep"]["beepLen"])
			except KeyError:
				continue

	@property
	def numpadUsedForColumnsNavigation(self):
		for profile in self.getApplicableProfiles():
			try:
				return is_boolean(profile["columnsReview"]["keyboard"]["useNumpadKeys"])
			except KeyError:
				continue

	@property
	def nextColumnsGroupKey(self):
		for profile in self.getApplicableProfiles():
			try:
				return profile["columnsReview"]["keyboard"]["switchChar"]
			except KeyError:
				continue

	@property
	def enabledModifiers(self):
		keys = dict()
		POSSIBLE_MODIFIERS = ("NVDA", "control", "alt", "shift", "windows")
		for profile in reversed(self.getApplicableProfiles()):
			for keyName in POSSIBLE_MODIFIERS:
				try:
					keys[keyName] = is_boolean(profile["columnsReview"]["gestures"][keyName])
				except KeyError:
					continue
		enabledKeys = dict(filter(lambda elem: elem[1], keys.items()))
		return "+".join(enabledKeys.keys())
