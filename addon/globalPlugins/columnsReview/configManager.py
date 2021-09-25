import config
try:
	from configobj.validate import is_boolean
except ImportError:
	from validate import is_boolean


class ConfigFromObject(object):

	def __init__(self, obj):
		self.obj = obj
		self.possibleTriggerName = "app:{0}".format(self.obj.appModule.appName)

	@property
	def triggersApplyForObj(self):
		return (
			list(config.conf.listProfiles())
			or config.conf.profileTriggersEnabled
			or not config.conf._suspendedTriggers
			or self.possibleTriggerName in config.conf.triggersToProfiles.keys()
		)

	def getApplicableProfiles(self):
		if self.triggersApplyForObj:
			res = []
			if len(config.conf.profiles) > 1:
				if config.conf._profileCache[config.conf.profiles[-1].name].manual:
					res.append(config.conf._profileCache[config.conf.profiles[-1].name])
			try:
				res.append(config.conf._profileCache[config.conf.triggersToProfiles[self.possibleTriggerName]])
			except KeyError:
				config.conf._getProfile(config.conf.triggersToProfiles[self.possibleTriggerName])
				res.append(config.conf._profileCache[config.conf.triggersToProfiles[self.possibleTriggerName]])
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
	def numpadUsedForColumnsNavigation(self):
		for profile in self.getApplicableProfiles():
			try:
				return is_boolean(profile["columnsReview"]["keyboard"]["useNumpadKeys"])
			except KeyError:
				continue
