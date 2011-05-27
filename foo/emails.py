from google.appengine.api.mail import EmailMessage
import settings

def get_invitation_email(address, key):
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


def get_first_trial_communication_email(account):
    """ prepare the invitation email message """

    SUBJECT = 'Foojal: First couple of days'
    EMAIL_CONTENT = """

Hello %s

Just checking it to see how you are liking your first few days of Foojal.com .
If you have any questions during your trial period please email us, we would
love to talk with you.

Your Team:
%s"""

    message = EmailMessage()
    message.sender = settings.SITE_EMAIL
    message.to = account.user.email()
    message.subject = SUBJECT
    message.body = EMAIL_CONTENT % (account.nickname, settings.SITE_EMAIL)
    return message


def get_second_trial_communication_email(account):
    """ prepare the invitation email message """

    SUBJECT = "Foojal: Don't lose out."
    EMAIL_CONTENT = """

Hello %s

Just checking it to see how you are liking your Foojal.com trail subscription.

Sign up today for a full year of Foojal.com for only $24.00 a year before we increase the price.
That's only $2.00 a month

If you have any questions during your trial period please email us, we would
love to talk with you.

Thank you, Kathy and Adam
%s"""

    message = EmailMessage()
    message.sender = settings.SITE_EMAIL
    message.to = account.user.email()
    message.subject = SUBJECT
    message.body = EMAIL_CONTENT % (account.nickname, settings.SITE_EMAIL)
    return message


def get_last_trial_communication_email(account):
    """ prepare the invitation email message """

    SUBJECT = "Foojal: Your trial is over!"
    EMAIL_CONTENT = """

Hello %s

We hope you liked your Foojal.com trail and that you will join us for a full year for only $24.00.

To get a full year subscription to the best online photo food journal go to your account page at http://app.foojal.com/account .

If you have any questions please email us, we would love to talk with you.

Thank you, Kathy and Adam

"""
    message = EmailMessage()
    message.sender = settings.SITE_EMAIL
    message.to = account.user.email()
    message.subject = SUBJECT
    message.body = EMAIL_CONTENT % account.nickname
    return message


def send_admin_notification(subject, data):
    message = EmailMessage()
    message.sender = settings.SITE_EMAIL
    message.to = settings.ADMIN_EMAIL
    message.subject = subject
    message.body = data
    message.send()

