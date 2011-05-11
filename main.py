#!/usr/bin/env python
import sys

from google.appengine.dist import use_library

use_library('django', '1.2')

from google.appengine.ext.webapp.util import run_wsgi_app
from foo.mail_handler import *
from foo.views import *

logging.info('Loading %s, app version = %s',
             __name__, os.getenv('CURRENT_VERSION_ID'))

ROUTES = [
        ('/', Today),
        ('/entry/map/(.*)', Map),
        ('/entry/new', NewEntry),
        ('/entry/(.*)', Entry),
        ('/tag/(.*)', Tag),
        ('/today', Today),
        ('/day/(.*)/(.*)/(.*)', Day),
        ('/week/(.*)/(.*)', Week),
        ('/month/(.*)/(.*)', Month),
        ('/account', Account),
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

#todo App write more test code.
#todo App fix the timezones
#todo App Test production billing system
#todo
#todo
#todo Marketing Slides video 
#todo 
#todo Add calender for easier navigation

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# todo Memcache - Added blacklist email list to memcache and update it every 1hr with cron job
# todo Email - Move all outbound emails to an email.py
# todo Admin - Add admin pages to the admin section see: http://code.google.com/appengine/docs/python/config/appconfig.html#Administration_Console_Custom_Pages
# todo Error - Add a custom error message to the application see: http://code.google.com/appengine/docs/python/config/appconfig.html#Custom_Error_Responses
# todo Admin - Add appstats to the admin see: http://code.google.com/appengine/docs/python/tools/appstats.html
# todo Admin - Need the ability to look at images and view the exif data from the photo.
# todo user - if a person deletes their last photo we should show the send us a sexy food photo page.

# todo - Facebook
# todo - Twitter
# todo - collage