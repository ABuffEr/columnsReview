"""Exercise the compatibility module without requiring a running NVDA instance."""

from pathlib import Path
import runpy
import sys
from types import ModuleType
import unittest
from unittest.mock import patch


COMPAT_PATH = Path(__file__).resolve().parents[2] / "addon" / "globalPlugins" / "columnsReview" / "compat.py"


class TestTextRegionCompatibility(unittest.TestCase):
	def loadCompat(self, brailleModules):
		version = ModuleType("buildVersion")
		version.version_year = 2027
		version.version_major = 1
		version.version_minor = 0
		modules = {
			"controlTypes": ModuleType("controlTypes"),
			"buildVersion": version,
			"braille.regions": None,
			"braille.regions.base": None,
		}
		modules.update(brailleModules)
		with patch.dict(sys.modules, modules):
			return runpy.run_path(
				str(COMPAT_PATH),
				init_globals={"ngettext": lambda singular, plural, count: plural},
			)

	def test_current_api_does_not_access_deprecated_alias(self):
		braille = ModuleType("braille")
		braille.__path__ = []

		def rejectLegacyAccess(name):
			if name == "TextRegion":
				raise AssertionError("The deprecated braille.TextRegion alias was accessed")
			raise AttributeError(name)

		braille.__getattr__ = rejectLegacyAccess
		regions = ModuleType("braille.regions")
		regions.__path__ = []
		base = ModuleType("braille.regions.base")
		base.TextRegion = type("CurrentTextRegion", (), {})
		compat = self.loadCompat(
			{
				"braille": braille,
				"braille.regions": regions,
				"braille.regions.base": base,
			},
		)
		self.assertIs(compat["TextRegion"], base.TextRegion)

	def test_legacy_braille_module(self):
		braille = ModuleType("braille")
		braille.TextRegion = type("LegacyTextRegion", (), {})
		compat = self.loadCompat({"braille": braille})
		self.assertIs(compat["TextRegion"], braille.TextRegion)

	def test_braille_package_without_regions(self):
		braille = ModuleType("braille")
		braille.__path__ = []
		braille.TextRegion = type("LegacyTextRegion", (), {})
		compat = self.loadCompat({"braille": braille})
		self.assertIs(compat["TextRegion"], braille.TextRegion)
