#!/usr/bin/env python
from google.appengine.dist import use_library
import foo

use_library('django', '1.2')

from google.appengine.ext.webapp.util import run_wsgi_app
from foo.mail_handler import *
from foo.tasks import *
from foo.views import *
from foo.jobs import *

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
        ('/account', foo.views.Account),
        ('/trial_message', SendTrialMessage),
        ('/invitation', SendInvite),
        ('/google_checkout/.*', google_checkout.GoogleListener),
        ('/purchase', PurchasePage),
        ('/invites/(.*)', Invite),
        ('/_ah/mail/invites.+', InvitesMailHandler),
        ('/_ah/mail/support.+', SupportMailHandler),
        ('/_ah/mail/.+', DefaultMailHandler),
        ('/admin/invitations', AdminInvitations),
        ]

application = webapp.WSGIApplication(ROUTES, debug=settings.ENABLE_DEBUG)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
