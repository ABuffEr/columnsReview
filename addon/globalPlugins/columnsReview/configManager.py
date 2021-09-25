import config
try:
	from configobj.validate import is_boolean
except ImportError:
	from validate import is_boolean


class ConfigFromObject(object):

	def __init__(self, obj):
		self.obj = obj

	@property
	def announceEmptyLists(self):
		possibleTriggerName = "app:{0}".format(self.obj.appModule.appName)
		if (
			not list(config.conf.listProfiles())
			or config.conf.profileTriggersEnabled is False
			or config.conf._suspendedTriggers
			or possibleTriggerName not in config.conf.triggersToProfiles.keys()
		):
			res = [config.conf]
		else:
			res = []
			if len(config.conf.profiles) > 1:
				if config.conf._profileCache[config.conf.profiles[-1].name].manual:
					res.append(config.conf._profileCache[config.conf.profiles[-1].name])
			try:
				res.append(config.conf._profileCache[config.conf.triggersToProfiles[possibleTriggerName]])
			except KeyError:
				config.conf._getProfile(config.conf.triggersToProfiles[possibleTriggerName])
				res.append(config.conf._profileCache[config.conf.triggersToProfiles[possibleTriggerName]])
			res.append(config.conf._profileCache[None])  # Default config
			res.append(config.conf)
		for profile in res:
			try:
				return is_boolean(profile["columnsReview"]["general"]["announceEmptyList"])
			except KeyError:
				continue
