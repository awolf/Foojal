import unittest
import foo.emails

class TestInvitationEmails(unittest.TestCase):
    """ Test the invitation emails """

    def setUp(self):
        self.address = "awolf@foojal.com"
        self.key = "123456789"
        self.message = foo.emails.MakeInvitationEmail(self.address, self.key)

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

