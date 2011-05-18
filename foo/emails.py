from google.appengine.api.mail import EmailMessage

def MakeInvitationEmail(address, key):
    """ prepare the invitation email message """

    EMAIL = 'Invites@foojals.appspotmail.com'
    SUBJECT = 'Your Foojal Invitation'
    URL = 'http://app.foojal.com/invites/'
    EMAIL_CONTENT = """
You have been invited to Foojal.com!

To accept this invitation, click the following link,
or copy and paste the URL into your browser's address
bar:

%s"""

    message = EmailMessage()
    message.sender = EMAIL
    message.to = address
    message.subject = SUBJECT
    message.body = EMAIL_CONTENT % URL + key
    return message


def Make