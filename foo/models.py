import logging
import uuid
import string

from datetime import timedelta, datetime
from google.appengine.api.taskqueue.taskqueue import add
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.api import taskqueue

def GetGeoPt(coordinate, GPSReference):
    try:
        coordinate  = coordinate.values
        GPSHour = coordinate[0]
        GPSHour = str(GPSHour)
        GPSHour = int(GPSHour)
        logging.info('GPSHour: ' + str(GPSHour))

        GPSSeconds = coordinate[2]
        GPSSeconds = str(GPSSeconds)
        GPSSeconds = int(GPSSeconds)
        logging.info('GPSSeconds: ' +str(GPSSeconds))

        GPSMinute = coordinate[1]
        GPSMinute = str(GPSMinute)
        try:
            GPSMinute = string.split(GPSMinute, "/")
            GPSMinuteDividend = GPSMinute[0]
            GPSMinuteDividend = float(GPSMinuteDividend)
            GPSMinuteDivisor  = GPSMinute[1]
            GPSMinuteDivisor  = float(GPSMinuteDivisor)
            GPSMinute  = GPSMinuteDividend / GPSMinuteDivisor
            logging.info('GPS Minute: ' + str(GPSMinute))
        except Exception, err:
            logging.error("Error fetching GPS coordinate " + str(err))
        else:
            pass

        GPS_Coordinate = GPSHour + (GPSMinute/60.0) + (GPSSeconds/3600.0)
    except Exception, err:
        logging.error("Error fetching latitude " + str(err))
        GPS_Coordinate = 0.0

    if  GPSReference == "W" or GPSReference == "S":
        GPS_Coordinate = GPS_Coordinate * -1.0

    return GPS_Coordinate

class Message(db.Model):
    owner = db.Key()
    sender = db.EmailProperty()
    to = db.StringProperty()
    subject = db.StringProperty()
    body = db.TextProperty()

    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)

    @classmethod
    def transfer_to_account(cls, sender, id):
        messages = Message.all()
        messages.filter("sender", sender)
        messages.filter("account_key", None)

        messages.fetch(500)

        for message in messages:
            message.account_key = id
            message.put()

class Photo(db.Model):
    owner = db.Key()
    sender = db.EmailProperty()

    location = db.GeoPtProperty()
    exif_data = db.BlobProperty()

    picture = db.BlobProperty()
    thumbnail = db.BlobProperty()

    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)

class Account(db.Model):
    user = db.UserProperty(auto_current_user_add=True)
    nickname = db.StringProperty()

    expiration_date = db.DateTimeProperty()

    address_list = db.StringListProperty()
    notify_by_email = db.BooleanProperty(default=True)

    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)

    @property
    def is_expired(self):
        return self.expiration_date < datetime.utcnow()
    
    @property
    def is_verified(self):
        """Whether the current account has been verified."""
        return self.user is not None

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

        return db.GqlQuery(
            "SELECT * FROM Account WHERE user = :1", user).get()

class BlackList(db.Model):
    email = db.EmailProperty()
    counter = db.IntegerProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)

    @classmethod
    def blacklist_email(cls, email):
        blacklist = cls.all().filter('email =', email).get()
        if blacklist:
            blacklist.counter += 1
            blacklist.put()
        else:
            blacklist = Blacklist()
            blacklist.email = email
            blacklist.counter = 1
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

        taskqueue.Queue('invite').add(taskqueue.Task(url='/invitation',params={'email' : invite.to_address, 'key': invite.unique_key}))
