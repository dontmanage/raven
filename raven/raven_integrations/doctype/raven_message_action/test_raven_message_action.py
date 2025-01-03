# Copyright (c) 2024, The Commit Company (Algocode Technologies Pvt. Ltd.) and Contributors
# See license.txt

# import dontmanage
from dontmanage.tests import IntegrationTestCase, UnitTestCase

# On IntegrationTestCase, the doctype test records and all
# link-field test record depdendencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]


class TestRavenMessageAction(UnitTestCase):
	"""
	Unit tests for RavenMessageAction.
	Use this class for testing individual functions and methods.
	"""

	pass


class TestRavenMessageAction(IntegrationTestCase):
	"""
	Integration tests for RavenMessageAction.
	Use this class for testing interactions between multiple components.
	"""

	pass
