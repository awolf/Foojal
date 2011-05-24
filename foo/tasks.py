from google.appengine.ext import webapp
import emails

class SendInvite(webapp.RequestHandler):
    """ Send out invitation to user """

    def post(self):
        address = self.request.get('email')
        key = self.request.get('key')

        message = emails.get_invitation_email(address, key)
        message.send()


class SendTrialMessage(webapp.RequestHandler):
    """ Send out invitation to user """

    def post(self):
        address = self.request.get('email')
        nickname = self.request.get('nickname')
        number = int(self.request.get('message'))

        message = None

        if number == 1:
            message = emails.get_first_trail_communication_email(address,nickname)
        elif number == 2:
            message = emails.get_second_trial_communication_email(address,nickname)
        elif number == 3:
            message = emails.get_last_trial_communication_email(address,nickname)

        message.send()
