#!/usr/bin/env python

from google.appengine.dist import use_library
use_library('django', '1.2')

# Python imports
import os
import cgi
import logging
from datetime import timedelta, datetime

# AppEngine imports
from django.http import HttpResponse
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template, Response
from google.appengine.ext.webapp.util import login_required
from google.appengine.runtime import DeadlineExceededError
from google.appengine.runtime import apiproxy_errors

# Local imports
import models
import settings

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
            params['account'] = models.Account.get_user_account()
            params['sign_out'] = users.create_logout_url("/")
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

    @login_required
    def get(self):

        values = {}

        account = models.Account.get_user_account()

        if account is not None:
            #values["account"] = account

            entries = models.Entry.all()
            entries.filter("owner", account.user)
            entries.order("-created")
            values["entries"] = entries.fetch(10)

        self.write_template(values)


class AccountPage(TemplatedPage):
    """ Sign ups and registration """

    @login_required
    def get(self):
        """ Account Display page """
        account = models.Account.get_user_account()

        if account:
            self.write_template({'account': account})
            return

        self.write_template({})

    def post(self):
        """Processes the signup creation request."""
        account = models.Account.get_user_account()

        if account is None:
            return self.redirect(users.create_login_url(self.request.get_full_path().encode('utf-8')))

        # Save the values from the form
        account.nickname = cgi.escape(self.request.get('name'))
        account.put()

        messages = models.Message.all()
        messages.filter("account_key", account.key().id())
        messages.order("-created")

        values = {
            'messages': messages.fetch(10),
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
        models.Entry.transfer_to_account(invitation.to_address, account.user)
        models.Photo.transfer_to_account(invitation.to_address, account.user)
        models.Invitation.remove_all_invites_by_email(invitation.to_address)
        self.redirect('/')

class PhotoHandler(webapp.RequestHandler):
    """Serves photos """

    def get(self):
        try:
            if self.request.get("id"):
                key = self.request.get("id")

                if 'If-Modified-Since' in self.request.headers:
                    self.response.set_status(304)
                else:
                    photo = models.Photo.get(key)

                    if photo:
                        self.response.headers['Content-Type'] = 'image/jpeg'
                        current_time = datetime.utcnow()
                        last_modified = current_time - timedelta(days=1)
                        self.response.headers['Last-Modified'] = last_modified.strftime('%a, %d %b %Y %H:%M:%S GMT')
                        self.response.headers['Expires'] = current_time + timedelta(days=30)
                        self.response.headers['Cache-Control']  = 'public, max-age=315360000'
                        self.response.headers['Date'] = current_time
                        self.response.out.write(photo.picture)
            else:
                logging.info("The image handler got an invalid message id of :" + self.request.get("id"))
                # Either "id" wasn't provided, or there was no image with that ID
                # in the datastore.
                self.redirect(settings.NO_IMAGE_URL)
        except:
            logging.error("Error fetching image " + str(err))
            self.redirect(settings.NO_IMAGE_URL)


class SendInvite(webapp.RequestHandler):
    """ Send out invitation to user """

    def post(self):
        address = self.request.get('email')
        key = self.request.get('key')
        message = mail.EmailMessage()
        message.sender = settings.INVITATION_EMAIL
        message.to = address
        message.subject = settings.INVITATION_SUBJECT
        message.body = settings.INVITATION_EMAIL_CONTENT % settings.INVITATION_URL + key
        message.send()