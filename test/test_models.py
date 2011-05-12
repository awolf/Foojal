import unittest
from google.appengine.ext.db import BadValueError
from google.appengine.api.users import User
from google.appengine.ext import testbed
from foo.models import *
from google.appengine.ext import db
import pytz

EMAIL = 'adam@adamjwolf.com'

class TestAccountModelDefaults(unittest.TestCase):
    account = None

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()
        self.account = Account()

    def tearDown(self):
        self.testbed.deactivate()

    def test_created_date_should_be_auto(self):
        assert self.account.created is not None

    def test_modified_date_should_be_auto_added(self):
        assert self.account is not None

    def test_notify_by_email_is_true(self):
        assert self.account.notify_by_email is True

    def test_timezone_is_Phoenix(self):
        assert self.account.timezone == str('America/Phoenix')

    def test_timezone_is_Phoenix(self):
        assert self.account.tz == pytz.timezone('America/Phoenix')

    def test_user(self):
        self.account.user = User(email='test@example.com')
        assert self.account.user is not None


class TestAccountExpiration(unittest.TestCase):
    account = None

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()
        self.account = Account.create_account_for_user(user=User(email='test@example.com'))

    def tearDown(self):
        self.testbed.deactivate()

    def test_account_is_not_expired(self):
        assert self.account.is_expired is False

    def test_account_is_expired(self):
        self.account.expiration_date = datetime.utcnow()
        assert self.account.is_expired


class TestAccountBlackListing(unittest.TestCase):
    account = None

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()
        self.account = Account.create_account_for_user(user=User(email='test@example.com'))

    def tearDown(self):
        self.testbed.deactivate()

    def test_account_should_be_blacklisted(self):
        self.account.expiration_date = datetime.utcnow() - timedelta(days=31)
        assert self.account.should_blacklist

    def test_account_should_not_be_blacklisted(self):
        self.account.expiration_date = datetime.utcnow() - timedelta(days=30)
        assert self.account.should_blacklist


class TestAccount(unittest.TestCase):
    account = None

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()
        self.account = Account.create_account_for_user(user=User(email='test@example.com'))

    def tearDown(self):
        self.testbed.deactivate()

    def test_if_account_is_verified(self):
        assert self.account.is_verified is True

    def test_adding_email_to_account(self):
        assert len(self.account.address_list) is 1
        self.account.add_email("awolf@foojal.com")
        assert len(self.account.address_list) is 2

    def test_fetching_account_by_email(self):
        data = Account.get_account_by_email("test@example.com")
        assert data

    def test_fetching_account_with_two_emails(self):
        self.account.add_email("awolf@foojal.com")
        data = Account.get_account_by_email("awolf@foojal.com")
        assert data


class TestInvitation(unittest.TestCase):
    invitation = None
    unique_key = "123456"
    unique_key2 = "987654"

    to_address = "test@example.com"

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_taskqueue_stub(_all_queues_valid=True)
        Invitation.send_invitation(self.to_address)

    def tearDown(self):
        self.testbed.deactivate()

    def test_get_invitation_by_unique_key(self):
        invites = db.GqlQuery("SELECT * FROM Invitation WHERE to_address = :1", self.to_address).fetch(1)
        key = invites[0].unique_key
        data = Invitation.get_invitation_by_unique_key(key)
        assert data

    def test_remove_all_remove_all_invitations(self):
        Invitation.send_invitation(self.to_address)
        invites = db.GqlQuery("SELECT * FROM Invitation WHERE to_address = :1", self.to_address).fetch(2)
        assert len(invites) is 2

        Invitation.remove_all_invites_by_email(self.to_address)
        invites = db.GqlQuery("SELECT * FROM Invitation WHERE to_address = :1", self.to_address).fetch(2)
        assert len(invites) is 0


class TestBlackList(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        BlackList.blacklist_email(EMAIL)

    def tearDown(self):
        self.testbed.deactivate()

    def test_New_BlackList_has_default_counter_of_1(self):
        """ The default counter for a new blacklist should be 1"""
        blacklist = BlackList(email=EMAIL)
        self.assertEqual(blacklist.email, EMAIL)
        self.assertEqual(blacklist.counter, 1)

    def test_BlackList_Requires_Email_Address(self):
        """ The email address is required for a blacklist model """
        self.failUnlessRaises(BadValueError, BlackList)

    def testInsertBlackListEntity(self):
        self.assertEqual(1, len(BlackList.all().fetch(2)))


    def testFindingBlackListByEmailAddress(self):
        blacklist = BlackList.get_blacklist_by_email(EMAIL)
        self.assertTrue(blacklist)

    def testIncrementBlackListCount(self):
        BlackList.blacklist_email(EMAIL)
        blacklist = BlackList.get_blacklist_by_email(EMAIL)
        self.assertTrue(blacklist.counter == 2)