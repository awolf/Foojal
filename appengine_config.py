import logging

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