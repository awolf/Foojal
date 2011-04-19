import logging
import uuid
import string

from datetime import timedelta, datetime
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import taskqueue

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
            GPSMinuteDivisor  = GPSMinute[1]
            GPSMinuteDivisor  = float(GPSMinuteDivisor)
            GPSMinute  = GPSMinuteDividend / GPSMinuteDivisor
            #logging.info('GPS Minute: ' + str(GPSMinute))
        except Exception, err:
            logging.error("Error fetching GPS coordinate " + str(err))
        else:
            pass

        GPS_Coordinate = GPSHour + (GPSMinute/60.0) + (GPSSeconds/3600.0)
    except Exception, err:
        logging.error("Error fetching GPS coordinate " + str(err))
        GPS_Coordinate = 0.0

    if  GPSReference == "W" or GPSReference == "S":
        GPS_Coordinate = GPS_Coordinate * -1.0

    return GPS_Coordinate

class Message(db.Model):
    owner = db.UserProperty()
    sender = db.EmailProperty()
    to = db.StringProperty()
    subject = db.StringProperty()
    body = db.TextProperty()
    exif_data = db.BlobProperty()
    picture = db.BlobProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)

class Entry(db.Model):
    owner = db.UserProperty()
    sender = db.EmailProperty()

    tags = db.StringListProperty()
    content = db.TextProperty()

    location = db.GeoPtProperty()
    exif_data = db.BlobProperty()

    picture_uid = db.StringProperty()
    thumbnail_uid = db.StringProperty()

    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)

    @classmethod
    def transfer_to_account(cls, sender, user):
        entries = Entry.all()
        entries.filter("sender", sender)
        entries.filter("owner", None)

        entries.fetch(500)

        for entry in entries:
            entry.owner = user
            entry.put()

class Photo(db.Model):
    owner = db.UserProperty()
    sender = db.EmailProperty()

    picture = db.BlobProperty()

    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)

    @classmethod
    def transfer_to_account(cls, sender, user):
        photos = Photo.all()
        photos.filter("sender", sender)
        photos.filter("owner", None)

        photos.fetch(500)

        for photo in photos:
            photo.owner = user
            photo.put()

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

        taskqueue.Queue('invite').add(taskqueue.Task(url='/invitation',params={'email' : invite.to_address, 'key': invite.unique_key}))
