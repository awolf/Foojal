#!/usr/bin/env python

from google.appengine.dist import use_library
use_library('django', '1.2')

from google.appengine.ext.webapp.util import run_wsgi_app
from foo.InvitesMailHandler import InvitesMailHandler
from foo.DefaultMailHandler import DefaultMailHandler
from foo.views import *

# Log a message each time this module get loaded.
logging.info('Loading %s, app version = %s',
             __name__, os.getenv('CURRENT_VERSION_ID'))

ROUTES = [
    ('/', MainPage),
    ('/account', AccountPage),
    ('/thumb', Thumbnailer),
    ('/invites/(.*)', Invite),
    ('/_ah/mail/invites.+', InvitesMailHandler),
    ('/_ah/mail/.+', DefaultMailHandler),
    ]

application = webapp.WSGIApplication(ROUTES, debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()