#!/usr/bin/env python
from datetime import datetime, date
from google.appengine.dist import use_library
import date_helper

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
import urllib2
import pytz

class TemplatedPage(webapp.RequestHandler):
    """Base class for templatized handlers."""

    def write_template(self, params, template_name=None):
        """Write out the template with the same name as the class name."""

        request = self.request
        params['request'] = request
        params['user'] = request.user
        params['is_admin'] = request.user_is_admin
        params['is_dev'] = settings.DEBUG
        params['current_uri'] = self.request.uri
        params['display'] = ['rotate-right', 'rotate-none', 'rotate-left']
        params['pincolor'] = settings.PIN_COLORS

        full_path = request.uri
        if request.user is None:
            params['sign_in'] = users.create_login_url(full_path)
        else:
            params['account'] = models.Account.get_user_account()
            params['sign_out'] = users.create_logout_url("/")
        try:
            if template_name:
                path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', template_name + ".html")
            else:
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


class RESTfulHandler(TemplatedPage):
    def post(self, *args):
        method = self.request.get('_method')

        if method == "put":
            self.put(*args)
        elif method == "delete":
            self.delete(*args)
        else:
            self.post(*args)


class NewEntry(TemplatedPage):
    @login_required
    def get(self):
        """ Account Display page """

        self.write_template({})

    def post(self):
        tags = self.request.get('tags')
        content = self.request.get('content')

        key = models.Entry.add_new_entry(tags, content)

        self.redirect('/entry/' + key.__str__())


class Today(TemplatedPage):
    @login_required
    def get(self):
        account = models.Account.get_user_account()
        if account is None:
            self.write_template({})
            return

        today = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(account.tz)
        data = date_helper.get_day_data(account, today.date())

        values = {
            "entries": models.Entry.get_entries_from_to(account, data['from_date'], data['to_date']),
            "heading": data['heading'],
            "display_date": data['target_day'],
            "previous_date_url": data['previous_date_url'],
            "next_date_url": data['next_date_url']
        }
        self.write_template(values, "Entries")


class Day(TemplatedPage):
    @login_required
    def get(self, day, month, year):
        account = models.Account.get_user_account()
        data = date_helper.get_day_data(account, date(int(year), month=int(month), day=int(day)))

        values = {
            "entries": models.Entry.get_entries_from_to(account, data['from_date'], data['to_date']),
            "heading": data['heading'],
            "display_date": data['target_day'],
            "previous_date_url": data['previous_date_url'],
            "next_date_url": data['next_date_url']
        }
        self.write_template(values, "Entries")


class Week(TemplatedPage):
    @login_required
    def get(self, week, year):
        account = models.Account.get_user_account()
        data = date_helper.get_week_data(account, int(week), int(year))

        values = {
            "entries": models.Entry.get_entries_from_to(account, data['from_date'], data['to_date']),
            "heading": data['heading'],
            "display_date": data['target_day'],
            "previous_date_url": data['previous_date_url'],
            "next_date_url": data['next_date_url']
        }
        self.write_template(values, "Entries")


class Month(TemplatedPage):
    @login_required
    def get(self, month, year):
        account = models.Account.get_user_account()
        data = date_helper.get_month_data(account, int(month), int(year))

        values = {
            "entries": models.Entry.get_entries_from_to(account, data['from_date'], data['to_date']),
            "heading": data['heading'],
            "display_date": data['target_day'],
            "previous_date_url": data['previous_date_url'],
            "next_date_url": data['next_date_url']
        }
        self.write_template(values, "Entries")


class Entry(RESTfulHandler):
    """ Entry detail page """

    def delete(self, key):
        models.Entry.delete_by_key(key)
        self.redirect('/')

    def put(self, key):
        account = models.Account.get_user_account()
        if not account:
            self.redirect(users.create_logout_url("www.foojal.com"))

        tags = self.request.get('tags')
        content = self.request.get('content')

        # Update the entry
        models.Entry.update_entry(key, tags, content)

        entity = models.Entry.get(key)
        values = {
            "entry": entity,
            "entries": models.Entry.get_entries_by_tags(tags=entity.tags, key=entity.key()),
            }

        self.write_template(values)


    @login_required
    def get(self, key):
        """ show journal entry for a single entry """
        request = self.request

        entry = models.Entry.get(key)
        entries = models.Entry.get_entries_by_tags(tags=entry.tags, key=entry.key())

        values = {
            "entry": entry,
            "entries": entries
        }

        self.write_template(values)


class Tag(TemplatedPage):
    """ Entry tag page """

    @login_required
    def get(self, tag):
        """ show journal entry for the sent id """

        tag = urllib2.unquote(tag)
        entries = models.Entry.get_entries_by_tags(tags=[tag])

        values = {
            "tag": tag,
            "entries": entries
        }

        self.write_template(values)


class Map(TemplatedPage):
    """ Map an entries using Google static map API """

    @login_required
    def get(self, key):
        """ show journal entry for the sent id """

        values = {
            "entry": models.Entry.get(key)
        }

        self.write_template(values)


class Account(TemplatedPage):
    """ Sign ups and registration """

    @login_required
    def get(self):
        """ Account Display page """

        account = models.Account.get_user_account()
        values = {
            'account': account,
            'countries': pytz.country_names,
            'timezones': pytz.country_timezones[account.country_code]}

        self.write_template(values)

    def post(self):
        """Processes the signup creation request."""

        account = models.Account.get_user_account()

        # Save the values from the form
        account.country_code = self.request.get('countries')
        account.timezone = self.request.get('timezones')
        account.nickname = cgi.escape(self.request.get('name'))
        account.put()

        values = {
            'countries': pytz.country_names,
            'timezones': pytz.country_timezones[account.country_code],
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
            cart.put()

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