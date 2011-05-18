from google.appengine.ext import webapp
import emails

class SendInvite(webapp.RequestHandler):
    """ Send out invitation to user """

    def post(self):
        address = self.request.get('email')
        key = self.request.get('key')

        message = emails.MakeInvitationEmail(address, key)
        message.send()