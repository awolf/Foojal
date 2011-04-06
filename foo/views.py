#!/usr/bin/env python

from google.appengine.dist import use_library
use_library('django', '1.2')

# Python imports
import os
import cgi
import logging

# AppEngine imports
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.runtime import DeadlineExceededError
from google.appengine.runtime import apiproxy_errors

# Local imports
import models

IS_DEV = os.environ['SERVER_SOFTWARE'].startswith('Dev')  # Development server

class TemplatedPage(webapp.RequestHandler):
    """Base class for templatized handlers."""

    def write_template(self, params):
        """Write out the template with the same name as the class name."""

        request = self.request
        params['request'] = request
        params['user'] = request.user
        params['is_admin'] = request.user_is_admin
        params['is_dev'] = IS_DEV
        params['current_uri'] = self.request.uri
        full_path = request.uri
        if request.user is None:
            params['sign_in'] = users.create_login_url(full_path)
        else:
            params['sign_out'] = users.create_logout_url("/")
            #account = models.Account.current_user_account
            #if account is not None:
            #params['xsrf_token'] = account.get_xsrf_token()
        try:
            path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates',
                                self.__class__.__name__ + '.html')

            self.response.out.write(template.render(path, params))
        except DeadlineExceededError:
            logging.exception('DeadlineExceededError')
            return HttpResponse('DeadlineExceededError', status=503)
        except apiproxy_errors.CapabilityDisabledError, err:
            logging.exception('CapabilityDisabledError: %s', err)
            return HttpResponse('Foojal: App Engine is undergoing maintenance. '
                                'Please try again in a while. ' + str(err),
                                status=503)
        except MemoryError:
            logging.exception('MemoryError')
            return HttpResponse('MemoryError', status=503)
        except AssertionError:
            logging.exception('AssertionError')
            return HttpResponse('AssertionError')
            #finally:
            #library.user_cache.clear() # don't want this sticking around


class MainPage(TemplatedPage):
    """Home page for Foojal"""

    def get(self):
        values = {}
        self.write_template(values)


class AccountPage(TemplatedPage):
    """ Sign ups and registration """

    @login_required
    def get(self):
        """ Account Display page """
        account = models.Account.get_user_account()

        if account is None:
            self.write_template({})
            return

        e = models.Event.all()
        e.filter("account_key", account.key().id())
        e.order("-created")

        values = {
            'events': e.fetch(20),
            'account': account
        }
        self.write_template(values)

    def post(self):
        """Processes the signup creation request."""

        account = models.Account.get_user_account()

        if account is None:
            return self.redirect(users.create_login_url(self.request.get_full_path().encode('utf-8')))

        # Save the values from the form
        account.nickname = cgi.escape(self.request.get('name'))
        account.put()

        e = models.Event.all()
        e.filter("account_key", account.key().id())
        e.order("-created")

        values = {
            'events': e.fetch(20),
            'account': account
        }
        self.write_template(values)

class Invite(TemplatedPage):
    """ Completes the sign up process """

    @login_required
    def get(self, unique_key):
        assert unique_key
        logging.info("The unique key:" + unique_key)

        if unique_key is None:
            self.redirect('/')
            return

        invitation = models.Invitation.get_invitation_by_unique_key(unique_key)

        if invitation is None:
            logging.error("The unique key:" + unique_key + " did not match any existing invitation keys")
            self.redirect('/')
            return

        account = models.Account.get_user_account()

        if not account:
            account = models.Account.create_account_for_user()

        account.add_email(invitation.to_address)
        models.Event.transfer_to_account(invitation.to_address, account.key().id())
        models.Invitation.remove_all_invites_by_email(invitation.to_address)
        self.redirect('/')

class Thumbnailer(webapp.RequestHandler):
    """Serves thumbnail images"""

    def get(self):
        if self.request.get("id"):
            event = models.Event.get_by_id(int(self.request.get("id")))

            if event:
                self.response.headers['Content-Type'] = 'image/jpeg'
                # Todo: lets set the cache header to something longer than a day
                self.response.out.write(event.thumbnail)
            else:
                logging.info("The thumbnailer got an invalid event id of :" + self.request.get("id"))
                # Either "id" wasn't provided, or there was no image with that ID
                # in the datastore.
                self.redirect('/public/images/noimage.gif')
