#!/usr/bin/env python
import urllib2

from google.appengine.dist import use_library

use_library('django', '1.2')

# Python imports
import os
import cgi
import logging

# AppEngine imports
from django.http import HttpResponse
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.runtime import DeadlineExceededError
from google.appengine.runtime import apiproxy_errors
from google.appengine.api.mail import EmailMessage

# Local imports
import models
import settings
import google_checkout

IS_DEV = os.environ['SERVER_SOFTWARE'].startswith('Dev')  # Development server

def unescape(s):
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    # this has to be last:
    s = s.replace("&amp;", "&")
    return s


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


class RESTfulHandler(TemplatedPage):
    def post(self, *args):
        method = self.request.get('_method')

        if method == "put":
            self.put(*args)
        elif method == "delete":
            self.delete(*args)
        else:
            self.post(*args)


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
            values["display"] = ['rotate-right', 'rotate-none', 'rotate-left']
            values["pincolor"] = settings.PIN_COLORS

        self.write_template(values)


class NewEntry(TemplatedPage):
    def get(self):
        """ Account Display page """

        self.write_template({})

    def post(self):
        tags = self.request.get('tags')
        content = self.request.get('content')
        account = models.Account.get_user_account()

        key = models.Entry.add_new_entry(tags, content, account)

        self.redirect('/entry/' + key.__str__())


class Entry(RESTfulHandler):
    """ Entry detail page """

    def delete(self, key):
        models.Entry.delete_by_key(key)
        self.redirect('/')

    def put(self, key):
        tags = self.request.get('tags')
        content = self.request.get('content')

        models.Entry.update_entry(key, tags, content)

        values = {}

        account = models.Account.get_user_account()
        entry = models.Entry.get(key)

        if not account or entry.owner != account.user:
            self.redirect(users.create_logout_url("www.foojal.com"))

        entries = models.Entry.all()
        entries.filter("owner", account.user)
        entries.filter("tags IN", entry.tags)
        entries.filter("__key__ !=", entry.key())

        values["entry"] = entry
        values["entries"] = entries.fetch(10)
        values["display"] = ['rotate-right', 'rotate-none', 'rotate-left']
        values["pincolor"] = settings.PIN_COLORS

        self.write_template(values)


    @login_required
    def get(self, key):
        """ show journal entry for the sent id """
        values = {}

        account = models.Account.get_user_account()
        entry = models.Entry.get(key)

        if not account or entry.owner != account.user:
            self.redirect(users.create_logout_url("www.foojal.com"))

        entries = models.Entry.all()
        entries.filter("owner", account.user)
        entries.filter("tags IN", entry.tags)
        entries.filter("__key__ !=", entry.key())

        values["entry"] = entry
        values["entries"] = entries.fetch(10)
        values["display"] = ['rotate-right', 'rotate-none', 'rotate-left']
        values["pincolor"] = settings.PIN_COLORS

        self.write_template(values)


class Tag(TemplatedPage):
    """ Entry tag page """

    @login_required
    def get(self, tag):
        """ show journal entry for the sent id """
        values = {}
        tag = urllib2.unquote(tag)

        account = models.Account.get_user_account()

        entries = models.Entry.all()
        entries.filter("owner", account.user)
        entries.filter("tags =", tag)
        entries.order("-created")

        values["tag"] = tag
        values["entries"] = entries.fetch(10)
        values["display"] = ['rotate-right', 'rotate-none', 'rotate-left']
        values["pincolor"] = settings.PIN_COLORS

        self.write_template(values)


class Map(TemplatedPage):
    """ Entry map page """

    @login_required
    def get(self, key):
        """ show journal entry for the sent id """

        values = {}

        entry = models.Entry.get(key)

        values["entry"] = entry
        values["display"] = ['rotate-right', 'rotate-none', 'rotate-left']
        values["pincolor"] = settings.PIN_COLORS

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

        values = {
            'success': 'Information Saved!',
            'account': account
        }
        self.write_template(values)


class PurchasePage(TemplatedPage):
    """ Sign ups and registration """

    @login_required
    def get(self):
        """ Purchase Display page """

        self.write_template({})

        def post(self):
            """ Start the purchase process"""

        cart = models.get_year_cart()

        url = google_checkout.post_shopping_cart(cart)

        if url:
            cart.url = url
            cart.put()
            self.redirect(url)
            return
        else:
            values = {
                'error': 'The shopping cart is down'}
            cart.status = 'Error' # we could use some more context

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
        models.Invitation.remove_all_invites_by_email(invitation.to_address)
        self.redirect('/')


class SendInvite(webapp.RequestHandler):
    """ Send out invitation to user """

    def post(self):
        address = self.request.get('email')

        key = self.request.get('key')
        message = EmailMessage()
        message.sender = settings.INVITATION_EMAIL
        message.to = address
        message.subject = settings.INVITATION_SUBJECT
        message.body = settings.INVITATION_EMAIL_CONTENT % settings.INVITATION_URL + key
        message.send()