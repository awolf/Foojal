from google.appengine.api import mail
from google.appengine.ext import webapp

class SendInvite(webapp.RequestHandler):
    """ Send out invitation to user """
    def post(self):
        address = self.request.get('email')
        key = self.request.get('key')
        message = mail.EmailMessage()
        message.sender = "Invites@foojalworld.appspotmail.com"
        message.to = address
        message.subject = "Your Foojal Invitation"
        message.body = """
You have been invited you to Foojal.com!

To accept this invitation, click the following link,
or copy and paste the URL into your browser's address
bar:

%s""" % "http://foojalworld.appspot.com/invites/" + key

        message.send()