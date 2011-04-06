import logging
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

class InvitesMailHandler(InboundMailHandler):
    """Handle incoming mail for invite mail account. """

    def receive(self, mail_message):
        logging.info("Invites mail handler received a message from: %s" % mail_message.sender)
        return
