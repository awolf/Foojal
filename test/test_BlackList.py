from google.appengine.ext.db import BadValueError
import foo.models
import unittest

from google.appengine.ext import testbed

EMAIL = 'adam@adamjwolf.com'

class TestBlackList(unittest.TestCase):

    def test_New_BlackList_has_default_counter_of_1(self):
        """ The default counter for a new blacklist should be 1"""
        blacklist = foo.models.BlackList(email=EMAIL)
        self.assertEqual(blacklist.email, EMAIL)
        self.assertEqual(blacklist.counter, 1)

    def test_BlackList_Requires_Email_Address(self):
        """ The email address is required for a blacklist model """
        self.failUnlessRaises(BadValueError,foo.models.BlackList)

class TestBlackListWithData(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        foo.models.BlackList.blacklist_email(EMAIL)
  
    def tearDown(self):
        self.testbed.deactivate()

    def testInsertBlackListEntity(self):
        self.assertEqual(1, len(foo.models.BlackList.all().fetch(2)))

    def testBlackListingEmailAddress(self):
        self.assertEqual(1, len(foo.models.BlackList.all().fetch(2)))

    def testFindingBlackListByEmailAddress(self):
        blacklist = foo.models.BlackList.get_blacklist_by_email(EMAIL)
        self.assertTrue(blacklist)

    def testIncrementBlackListCount(self):
        foo.models.BlackList.blacklist_email(EMAIL)
        blacklist = foo.models.BlackList.get_blacklist_by_email(EMAIL)
        self.assertTrue(blacklist.counter == 2)
