import unittest
from google.appengine.api.users import User
import foo.emails
from foo.models import Account
from google.appengine.ext import testbed

test_code = """

        taskqueue.Queue('mail').add(
            taskqueue.Task(url='/trial_message', params={'email': 'adamjwolf@me.com', 'nickname': 'adam wolf', 'message': '3'}))
"""

class TestInvitationEmails(unittest.TestCase):
    """ Test the invitation emails """

    def setUp(self):
        self.address = "awolf@foojal.com"
        self.key = "123456789"
        self.message = foo.emails.get_invitation_email(self.address, self.key)

    def test_message_body_contains_invitation_link(self):
        """ test that the invitation email has a valid URL """

        URL = 'http://app.foojal.com/invites/'

        assert self.message
        assert self.message.body.find(URL + self.key)

    def test_message_is_addressed_correctly(self):
        """ test that the invitation email has a valid address """

        assert self.message
        assert self.message.to == self.address

    def test_message_is_from_invites_at_foojal(self):
        """ test that the from address in invitation
        emails comes from Invites@foojals.appspotmail.com """

        assert self.message
        assert self.message.sender == 'Invites@foojals.appspotmail.com'


class TestFirstTrialEmail(unittest.TestCase):
    """ Test the first email sent to trial accounts """


    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()
        self.account = Account.create_account_for_user(user=User(email='awolf@foojal.com'))
        self.account.nickname = "Adam"
        
        self.message = foo.emails.get_first_trial_communication_email(self.account)

    def test_message_body_contains_nickname(self):
        """ test that the users nickname is
        added to email message"""
        
        assert self.message
        assert self.message.body.find(self.account.nickname)

    def test_message_is_addressed_correctly(self):
        """ test that the message is address to the user """
        
        assert self.message
        assert self.message.to == self.account.user.email()

class TestSecondTrialEmail(unittest.TestCase):
    """ Test the second email sent to trial accounts """

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()
        self.account = Account.create_account_for_user(user=User(email='awolf@foojal.com'))
        self.account.nickname = "Adam"

        self.message = foo.emails.get_second_trial_communication_email(self.account)

    def test_message_body_contains_nickname(self):
        """ test that the users nickname is
        added to email message"""

        assert self.message
        assert self.message.body.find(self.account.nickname)

    def test_message_is_addressed_correctly(self):
        """ test that the message is address to the user """

        assert self.message
        assert self.message.to == self.account.user.email()

    def test_message_contains_price(self):
        
        assert self.message
        assert self.message.body.find("$24.00")


class TestLastTrialEmail(unittest.TestCase):
    """ Test the last email sent to trial accounts """

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()
        self.account = Account.create_account_for_user(user=User(email='awolf@foojal.com'))
        self.account.nickname = "Adam"

        self.message = foo.emails.get_last_trial_communication_email(self.account)

    def test_message_body_contains_nickname(self):
        """ test that the users nickname is
        added to email message"""

        assert self.message
        assert self.message.body.find(self.account.nickname)


    def test_message_is_addressed_correctly(self):
        """ test that the message is address to the user """

        assert self.message
        assert self.message.to == self.account.user.email()

    def test_message_contains_price(self):

        assert self.message
        assert self.message.body.find("$24.00")