from datetime import date
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


class TestEntries(unittest.TestCase):
    account = None
    email_to = 'test@example.com'
    content = "Eat to many wings at the party"
    tags = "Dinner party spicy beer"
    tag_list = [u'dinner', u'party', u'spicy', u'beer']

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()
        self.account = Account.create_account_for_user(user=User(email=self.email_to))

    def tearDown(self):
        self.testbed.deactivate()

    def test_add_entry(self):
        entries = Entry.all().get()
        assert entries is None

        entry = Entry()
        entry.owner = self.account.user
        entry.put()

        entries = Entry.all().fetch(10)
        assert len(entries) is 1

    def test_update_entry(self):
        entry = Entry()
        entry.owner = self.account.user
        entry.put()

        assert entry.content is None
        assert entry.tags == []

        entry.update_entry(entry.key(), self.tags, self.content, self.account)

        entries = Entry.all().fetch(1)
        result = entries[0]
        assert result.content == self.content
        assert result.tags == self.tag_list

    def test_adding_new_entry(self):
        key = Entry.add_new_entry(self.tags, self.content, self.account)

        entry = Entry.get(key)

        assert entry
        assert entry.content == self.content
        assert entry.tags == self.tag_list

    def test_get_all_entries_by_tag(self):
        Entry.add_new_entry(self.tags, self.content, self.account)
        Entry.add_new_entry(self.tags, self.content, self.account)
        Entry.add_new_entry(self.tags, self.content, self.account)

        entries = Entry.get_entries_by_tags(tags=['dinner'], account=self.account)

        assert len(entries) == 3

    def test_get_all_entries_by_tag(self):
        Entry.add_new_entry(self.tags, self.content, self.account)
        key = Entry.add_new_entry(self.tags, self.content, self.account)
        Entry.add_new_entry(self.tags, self.content, self.account)

        entries = Entry.get_entries_by_tags(tags=['dinner'], key=key, account=self.account)

        assert len(entries) == 2

    def test_get_all_entries_by_tag_limit_2(self):
        Entry.add_new_entry(self.tags, self.content, self.account)
        Entry.add_new_entry(self.tags, self.content, self.account)
        Entry.add_new_entry(self.tags, self.content, self.account)

        entries = Entry.get_entries_by_tags(tags=['dinner'], count=2, account=self.account)

        assert len(entries) == 2


class TestEntriesTags(unittest.TestCase):
    account = None
    email_to = 'test@example.com'

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()
        self.account = Account.create_account_for_user(user=User(email=self.email_to))

    def tearDown(self):
        self.testbed.deactivate()

    def test_tags_with_uppercase_letters(self):
        entry = Entry()
        entry.owner = self.account.user
        entry.put()

        Entry.update_entry(entry.key(), "THIS IS CAPITALIZED", "", self.account)

        entry = Entry.get(entry.key())

        assert entry.tags == [u'this', u'is', u'capitalized']

    def test_tags_with_extra_spaces(self):
        entry = Entry()
        entry.owner = self.account.user
        entry.put()

        Entry.update_entry(entry.key(), " THIS  is  CAPITALIZED ", "", self.account)

        entry = Entry.get(entry.key())

        assert entry.tags == [u'this', u'is', u'capitalized']


class TestEntriesTags(unittest.TestCase):
    account = None
    email_to = 'test@example.com'

    content = "Eat to many wings at the party"
    tags = "Dinner party spicy beer"

    dates = [
        datetime(2011, 1, 12),
        datetime(2011, 4, 12)
    ]

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()
        self.account = Account.create_account_for_user(user=User(email=self.email_to))

        for date in self.dates:
            entry = Entry()
            entry.owner = self.account.user
            entry.created = date.replace(tzinfo=self.account.tz)
            entry.put()

    def tearDown(self):
        self.testbed.deactivate()

    def test_should_return_two_entries(self):
        entries = Entry.get_entries_from_to(
                            self.account,
                            from_date=datetime(2011,1,1).replace(tzinfo=pytz.utc),
                            to_date=datetime(2011,5,1).replace(tzinfo=pytz.utc))

        assert len(entries) == 2

    def test_should_not_return_other_users_data(self):
        account_b = Account.create_account_for_user(user=User(email='someone@else.com'))
        entry = Entry()
        entry.owner = account_b.user
        entry.created = datetime(2011,1,12).replace(tzinfo=account_b.tz)
        entry.put()

        entries = Entry.get_entries_from_to(
                            self.account,
                            from_date=datetime(2011,1,1).replace(tzinfo=pytz.utc),
                            to_date=datetime(2011,5,1).replace(tzinfo=pytz.utc))

        assert len(entries) == 2

    def test_should_return_results_in_users_timezone(self):
        entries = Entry.get_entries_from_to(
                            self.account,
                            from_date=datetime(2011,1,1).replace(tzinfo=pytz.utc),
                            to_date=datetime(2011,5,1).replace(tzinfo=pytz.utc))
        
        for entry in entries:
            assert entry.created == entry.created.astimezone(self.account.tz)
