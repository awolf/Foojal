import logging
import uuid
import string

from datetime import timedelta, datetime
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import mail

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

class Event(db.Model):
    account_key = db.IntegerProperty()
    sender = db.StringProperty()
    to = db.StringProperty()
    subject = db.StringProperty()
    body = db.TextProperty()

    latitude = db.TextProperty()
    latitudeReference = db.TextProperty()

    longitude = db.TextProperty()
    longitudeReference = db.TextProperty()

    location = db.GeoPtProperty()

    exif_text = db.TextProperty()

    picture_name = db.StringProperty()
    picture = db.BlobProperty()
    thumbnail = db.BlobProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)

    @classmethod
    def transfer_to_account(cls, sender, id):
        e = Event.all()
        e.filter("sender", sender)
        e.filter("account_key", None)

        e.fetch(500)

        for event in e:
            event.account_key = id
            event.put()


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

        message = mail.EmailMessage()
        message.sender = "Invites@foojalworld.appspotmail.com"
        message.to = invite.to_address
        message.subject = "Your Foojal Invitation"
        message.body = """
You have been invited you to Foojal.com!

To accept this invitation, click the following link,
or copy and paste the URL into your browser's address
bar:

%s""" % "http://foojalworld.appspot.com/invites/" + invite.unique_key

        message.send()


class Photo(db.Model):
    account_key = db.Key()
    picture_name = db.StringProperty()
    picture = db.BlobProperty()
    thumbnail = db.BlobProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)