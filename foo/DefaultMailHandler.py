#!/usr/bin/env python

from google.appengine.dist import use_library
use_library('django', '1.2')

# Python imports
import logging
import string
from StringIO import StringIO

# AppEngine imports
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext import db
from google.appengine.api import images


# Local imports
import models
import EXIF

def goodDecode(encodedPayload):
    if not hasattr(encodedPayload, 'encoding'):
        return encodedPayload
    encoding = encodedPayload.encoding
    payload = encodedPayload.payload
    if encoding and encoding.lower() != '7bit':
        payload = payload.decode(encoding)
    return payload

class DefaultMailHandler(InboundMailHandler):
    """Handle incoming mail from users """

    def receive(self, mail_message):



        logging.info("Received a message from: " + mail_message.sender)
        sender = mail_message.sender
        account = models.Account.get_account_by_email(sender)

        account_id = None

        if account:
            account_id = account.key().id()
            if account.is_expired:
                logging.info("Receiving email from " + mail_message.sender + " an expired account that is verified = " + str(account.is_verified))
                return

        else:
            models.Invitation.send_invitation(sender)

        event = models.Event()
        event.account_key = account_id
        event.sender = sender
        event.to = mail_message.to
        if hasattr(mail_message, 'subject'):
            event.subject = mail_message.subject

        # Get the body text out of the email
        plaintext_bodies = mail_message.bodies('text/plain')
        body_text = ""
        for content_type, body in plaintext_bodies:
            body_text = body_text + body.decode() + " "
        event.body = str(body_text)

        try:
            attachments = mail_message.attachments
            orientation = None
            image_data = None
            if attachments:
                logging.info("We have attachments in this email: ")

                try:
                    # todo: Adam How about we check that the first attachment is a photo!
                    # Get the image data from the first attachment
                    image_data = goodDecode(attachments[0][1])

                    #logged the size of the incoming image
                    logging.info("attachment length " + str(len(image_data)))

                    # get some exif love from the first attachments
                    tags = EXIF.process_file(StringIO(str(image_data)))
                    logging.info("start decoding exif tags ")
                    
                    orientation = str(tags["Image Orientation"])

                    latitude = str(tags['GPS GPSLatitude'])
                    latitudeReference = str(tags['GPS GPSLatitudeRef'])
                    latitudeCoordinate = models.GetGeoPt(tags['GPS GPSLatitude'],latitudeReference)
                    logging.info("GPS Latitude results" + str(latitudeCoordinate))

                    longitude = str(tags['GPS GPSLongitude'])
                    longitudeReference = str(tags['GPS GPSLongitudeRef'])
                    longitudeCoordinate = models.GetGeoPt(tags['GPS GPSLongitude'],longitudeReference)
                    logging.info("GPS Longitude results " + str(longitudeCoordinate))

                    event.latitude = latitude
                    event.latitudeReference = latitudeReference
                    event.longitude = longitude
                    event.longitudeReference = longitudeReference
                    event.location = db.GeoPt(latitudeCoordinate, longitudeCoordinate)

                    tagText = ""
                    for key, value in tags.items():
                        tagText = tagText + " " + str(key) + " := " + str(value)
                    event.exif_text = tagText

                    logging.info("end decoding exif tags ")
                except Exception, err:
                    logging.error("Error fetching tags " + str(err))

                img = images.Image(image_data)
                img.resize(width=600,height=600)

                if orientation == "Rotated 90 CW":
                    img.rotate(90)
                    logging.info("image rotated 90%")
                elif orientation == "Rotated 180":
                    img.rotate(180)
                    logging.info("image rotated 180%")
                elif orientation == "Rotated 90 CCW":
                    img.rotate(270)
                    logging.info("image rotated 260%")

                #img.im_feeling_lucky()
                thumbnail = img.execute_transforms(output_encoding=images.JPEG)

                logging.info("Thumbnail created: ")

                event.thumbnail = db.Blob(thumbnail)
                event.picture_name = attachments[0][0]
        except Exception, err:
            logging.error("Error working with attachments " + str(err))

        event.put()