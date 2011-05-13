import os
import unittest
from foo.views import Today
from webtest import TestApp
from google.appengine.ext import webapp

from google.appengine.api import users
from webob import Request

class AddUserToRequestMiddleware(object):
    """Add a user object and a user_is_admin flag to each request."""

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        req = Request(environ)

        # Add some helpfull things to the request.
        req.user = users.get_current_user()
        req.user_is_admin = str(users.is_current_user_admin())

        resp = req.get_response(self.app)
        return resp(environ, start_response)


def webapp_add_wsgi_middleware(app):
    app = AddUserToRequestMiddleware(app)
    return app


class IndexTest(unittest.TestCase):
    def setUp(self):
        self.application = webapp.WSGIApplication([('/', Today)], debug=True)

    def test_default_page(self):
        os.environ['USER_EMAIL'] = 'test@example.com'
        os.environ['REMOTE_USER'] = 'test@example.com'
        os.environ['USER_IS_ADMIN'] = '1'
        os.environ['USER_ID'] = '1'
        os.environ['AUTH_DOMAIN'] = 'foojalworld'
        app = TestApp(webapp_add_wsgi_middleware(self.application))

        response = app.get('/')
        self.assertEqual('200 OK', response.status)
        #self.assertTrue('Hello, World!' in response)

#  def test_page_with_param(self):
#      app = TestApp(self.application)
#      response = app.get('/?name=Bob')
#      self.assertEqual('200 OK', response.status)
#      self.assertTrue('Hello, Bob!' in response)
