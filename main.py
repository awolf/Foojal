#!/usr/bin/env python

from google.appengine.dist import use_library
use_library('django', '1.2')

from google.appengine.ext.webapp.util import run_wsgi_app
from foo.mail_handler import *
from foo.views import *

# Log a message each time this module get loaded.
logging.info('Loading %s, app version = %s',
             __name__, os.getenv('CURRENT_VERSION_ID'))

ROUTES = [
    ('/', MainPage),
    ('/account', AccountPage),
    ('/photo', PhotoHandler),
    ('/invitation', SendInvite),
    ('/google_checkout/.*', googlecheckout.GoogleListener),
    ('/invites/(.*)', Invite),
    ('/_ah/mail/invites.+', InvitesMailHandler),
    ('/_ah/mail/.+', DefaultMailHandler),
    ]

application = webapp.WSGIApplication(ROUTES, debug=settings.ENABLE_DEBUG)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()

# todo Memcache - Added blacklist email list to memcache and update it every 1hr with cron job
# todo Email - Move all outbound emails to an email.py