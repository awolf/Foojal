
from google.appengine.dist import use_library
import pytz

use_library('django', '1.2')

from datetime import datetime
from time import strftime
import os
import unittest
from appengine_config import webapp_add_wsgi_middleware
from foo.views import Today
from webtest import TestApp
from google.appengine.ext import webapp
from google.appengine.ext import testbed
from google.appengine.api.users import User
from foo.models import Account

def addAccount(email):
    Account.create_account_for_user(User(email='test@example.com'))


class IndexTest(unittest.TestCase):
    def setUp(self):
        os.environ['USER_EMAIL'] = 'test@example.com'
        os.environ['USER_IS_ADMIN'] = '1'
        self.application = webapp_add_wsgi_middleware(webapp.WSGIApplication([('/', Today)], debug=True))

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_default_page(self):
        addAccount('test@example.com')
        app = TestApp(self.application)
        response = app.get('/')
        #print response
        date = strftime("%A %B %d", datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone("America/Phoenix")).timetuple())
        #print date
        self.assertEqual('200 OK', response.status)
        self.assertTrue(date in response)

#  def test_page_with_param(self):
#      app = TestApp(self.application)
#      response = app.get('/?name=Bob')
#      self.assertEqual('200 OK', response.status)
#      self.assertTrue('Hello, Bob!' in response)
