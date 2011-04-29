#!/usr/bin/env python

from google.appengine.dist import use_library

use_library('django', '1.2')

from google.appengine.ext.webapp.util import run_wsgi_app
from foo.mail_handler import *
from foo.views import *

logging.info('Loading %s, app version = %s',
             __name__, os.getenv('CURRENT_VERSION_ID'))

ROUTES = [
        ('/', MainPage),
        ('/entry/(.*)', Entry),
        ('/account', AccountPage),
        ('/invitation', SendInvite),
        ('/google_checkout/.*', google_checkout.GoogleListener),
        ('/purchase', PurchasePage),
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
# todo Admin - Add admin pages to the admin section see: http://code.google.com/appengine/docs/python/config/appconfig.html#Administration_Console_Custom_Pages
# todo Error - Add a custom error message to the application see: http://code.google.com/appengine/docs/python/config/appconfig.html#Custom_Error_Responses
# todo Admin - Add appstats to the admin see: http://code.google.com/appengine/docs/python/tools/appstats.html
# todo Admin - Need the ability to look at images and view the exif data from the photo.
