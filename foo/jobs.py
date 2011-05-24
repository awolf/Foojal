import logging
from google.appengine.ext import webapp
from foo.models import Account

class SendTrialMessage(webapp.RequestHandler):
    """ Send out trial expiring notifications to trial users """

    def post(self):
        logging.info("Starting trial account messaging")
        Account.send_trial_notifications()
        logging.info("Ending trial account messaging")
