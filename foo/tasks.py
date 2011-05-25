from google.appengine.ext import webapp
import emails

class SendInvite(webapp.RequestHandler):
    """ Send out invitation to user """

    def post(self):
        address = self.request.get('email')
        key = self.request.get('key')

        message = emails.get_invitation_email(address, key)
        message.send()

        emails.send_admin_notification("Invitation email sent", "Email: %s Key: %s" % (address, key))