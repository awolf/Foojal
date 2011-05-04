import logging
import uuid
import string
import pytz
import settings

from datetime import timedelta, datetime
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import taskqueue
from google.appengine.ext import blobstore

def save_communication(text):
    CartCommunications(text=text).put()


def generate_purchase_key():
    "for generating a unique key for new Purchase"
    key = str(uuid.uuid4())
    key = key.replace("-", "")
    key = '%s-%s' % (get_new_id(), key[0:12])
    get_new_id()
    return key


def get_new_id():
    'get the last id for Purchase Model'
    query = Purchase.all()
    query.order('-purchase_id')
    last_item = query.get()
    #if no earlier cart or purchase then we make the id equal 1
    try: id = last_item.purchase_id + 1
    except: id = settings.PURCHASE_ID_START
    return id


def get_year_cart():
    """Create an invoice for one year."""

    cart = Cart(price=24.00, number_of_days=365, title="One Year Subscription.")
    cart.description = "Subscription to Foojal your photo food journal"
    cart.put()
    return cart


def GetGeoPt(coordinate, GPSReference):
    try:
        GPSHour = coordinate[0]
        GPSHour = int(GPSHour)
        #logging.info('GPSHour: ' + str(GPSHour))

        GPSSeconds = coordinate[2]
        GPSSeconds = float(GPSSeconds)
        #logging.info('GPSSeconds: ' +str(GPSSeconds))

        GPSMinute = coordinate[1]
        GPSMinute = str(GPSMinute)
        try:
            GPSMinute = string.split(GPSMinute, "/")
            GPSMinuteDividend = GPSMinute[0]
            GPSMinuteDividend = float(GPSMinuteDividend)
            GPSMinuteDivisor = GPSMinute[1]
            GPSMinuteDivisor = float(GPSMinuteDivisor)
            GPSMinute = GPSMinuteDividend / GPSMinuteDivisor
            #logging.info('GPS Minute: ' + str(GPSMinute))
        except Exception, err:
            logging.error("Error fetching GPS coordinate " + str(err))
        else:
            pass

        GPS_Coordinate = GPSHour + (GPSMinute / 60.0) + (GPSSeconds / 3600.0)
    except Exception, err:
        logging.error("Error fetching GPS coordinate " + str(err))
        GPS_Coordinate = 0.0

    if  GPSReference == "W" or GPSReference == "S":
        GPS_Coordinate = GPS_Coordinate * -1.0

    return GPS_Coordinate


class UtcDateTimeProperty(db.DateTimeProperty):
    '''Marks DateTimeProperty values returned from the datastore as UTC. Ensures
    all values destined for the datastore are converted to UTC if marked with an
    alternate Timezone.

    Inspired by
    http://www.letsyouandhimfight.com/2008/04/12/time-zones-in-google-app-engine/
    http://code.google.com/appengine/articles/extending_models.html
    '''

    def get_value_for_datastore(self, model_instance):
        '''Returns the value for writing to the datastore. If value is None,
        return None, else ensure date is converted to UTC. Note Google App
        Engine already does this. Called by datastore
        '''

        date = super(UtcDateTimeProperty,
                     self).get_value_for_datastore(model_instance)
        if date:
            if date.tzinfo:
                return date.astimezone(pytz.utc)
            else:
                return date.replace(tzinfo=pytz.utc)
        else:
            return None

    def make_value_from_datastore(self, value):
        '''Returns the value retrieved from the datastore. Ensures all dates
        are properly marked as UTC if not None'''

        if value is None:
            return None
        else:
            return value.replace(tzinfo=pytz.utc)


class Message(db.Model):
    owner = db.UserProperty()
    sender = db.EmailProperty()
    to = db.StringProperty()
    subject = db.StringProperty()
    body = db.TextProperty()

    picture_url = db.StringProperty()
    picture_key = db.StringProperty()
    picture_width = db.IntegerProperty()
    picture_height = db.IntegerProperty()

    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)


class Account(db.Model):
    user = db.UserProperty(auto_current_user_add=True)
    nickname = db.StringProperty()

    country_code = db.StringProperty(default="us")
    timezone = db.StringProperty(default="America/Phoenix")

    expiration_date = db.DateTimeProperty()

    address_list = db.StringListProperty()
    notify_by_email = db.BooleanProperty(default=True)

    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)

    @property
    def tz(self):
        return pytz.timezone(self.timezone)

    @property
    def is_expired(self):
        return self.expiration_date < datetime.utcnow()

    @property
    def is_verified(self):
        """Whether the current account has been verified."""
        return self.user is not None

    @property
    def should_blacklist(self):
        """Whether the current account should be blacklisted."""
        return self.expiration_date < (datetime.utcnow() + timedelta(days=-30))

    def add_email(self, email):
        if email not in self.address_list:
            self.address_list.append(email)
        self.put()

    @classmethod
    def get_account_by_email(cls, email):
        """Get the Account for an email address, or return None."""
        assert email

        return db.GqlQuery("SELECT * FROM Account WHERE address_list = :1", email).get()

    @classmethod
    def create_account_for_user(cls):
        user = users.get_current_user()
        account = Account()
        account.nickname = user.nickname()
        account.address_list.append(user.email())
        account.expiration_date = datetime.utcnow() + timedelta(days=7)
        account.put()
        return account

    @classmethod
    def get_user_account(cls):
        """Get the Account for a user"""
        user = users.get_current_user()

        account = db.GqlQuery(
            "SELECT * FROM Account WHERE user = :1", user).get()

        return account


class Entry(db.Model):
    owner = db.UserProperty()
    sender = db.EmailProperty()

    tags = db.StringListProperty()
    content = db.TextProperty()

    location = db.GeoPtProperty()
    exif_data = db.BlobProperty()

    picture_url = db.StringProperty()
    picture_key = db.StringProperty()

    created = UtcDateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)

    def has_picture(self):
        return self.picture_url

    @classmethod
    def transfer_to_account(cls, sender, user):
        entries = Entry.all()
        entries.filter("sender", sender)
        entries.filter("owner", None)

        entries.fetch(500)

        for entry in entries:
            entry.owner = user
            entry.put()

    @classmethod
    def delete_by_key(cls, key):
        entry = cls.get(key)
        account = Account.get_user_account()

        if entry.owner == account.user:
            if entry.has_picture():
                picture = blobstore.BlobInfo.get(entry.picture_key)
                if picture:
                    picture.delete()
            entry.delete()

    @classmethod
    def update_entry(cls, key, tags, content):
        entry = cls.get(key)
        account = Account.get_user_account()

        if entry.owner == account.user:
            entry.content = content.strip()

            entry.tags = [tag for tag in tags.strip().lower().split(' ') if tag]
            entry.put()

    @classmethod
    def add_new_entry(cls, tags, content, account):
        entry = Entry()
        entry.owner = account.user
        entry.content = content.strip()
        entry.tags = [tag for tag in tags.strip().lower().split(' ') if tag]
        entry.put()

        return entry.key()


class BlackList(db.Model):
    email = db.EmailProperty(required=True)
    counter = db.IntegerProperty(default=1)
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)

    @classmethod
    def get_blacklist_by_email(cls, email):
        """ Get the Account for an email address, or return None.
        """
        assert email

        return db.GqlQuery("SELECT * FROM BlackList WHERE email = :1", email).get()


    @classmethod
    def blacklist_email(cls, email):
        assert email

        blacklist = BlackList.all().filter('email =', email).get()
        if blacklist:
            blacklist.counter += 1
            blacklist.put()
        else:
            blacklist = BlackList(email=email)
            blacklist.email = email
            blacklist.put()


class Invitation(db.Model):
    unique_key = db.StringProperty()
    to_address = db.EmailProperty()
    account_key = db.Key()
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)

    @classmethod
    def get_invitation_by_unique_key(cls, unique_key):
        assert unique_key
        return db.GqlQuery("SELECT * FROM Invitation WHERE unique_key = :1", unique_key).get()

    @classmethod
    def remove_all_invites_by_email(cls, email):
        invites = db.GqlQuery("SELECT * FROM Invitation WHERE to_address = :1", email).fetch(500)
        db.delete(invites)

    @classmethod
    def send_invitation(cls, email):
        """ Send an invitation to the email address"""
        assert email

        # Create and send email invitation
        invite = Invitation()
        invite.unique_key = str(uuid.uuid1())
        invite.to_address = email
        invite.put()

        taskqueue.Queue('invite').add(
            taskqueue.Task(url='/invitation', params={'email': invite.to_address, 'key': invite.unique_key}))


class Cart(db.Model):
    user = db.UserProperty(auto_current_user_add=True)

    url = db.LinkProperty()

    status = db.StringProperty(default='New')

    title = db.StringProperty()
    description = db.StringProperty()
    price = db.FloatProperty(required=True)
    number_of_days = db.IntegerProperty(required=True)

    request = db.TextProperty()
    response = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)


class Purchase(db.Model):
    user = db.UserProperty()

    google_order_number = db.IntegerProperty()
    purchase_email = db.EmailProperty()
    purchase_id = db.IntegerProperty()

    total_charge_amount = db.FloatProperty()
    charge_date = db.DateTimeProperty()
    item = db.StringProperty()
    quantity = db.IntegerProperty()
    number_of_days = db.IntegerProperty()

    errors = db.TextProperty()
    processed = db.BooleanProperty(default=False)
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)


class CartCommunications(db.Model):
    text = db.TextProperty()

    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)