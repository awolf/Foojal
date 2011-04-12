#!/usr/bin/env python
from google.appengine.dist import use_library
use_library('django', '1.2')

# Python imports
import logging
import pickle
from StringIO import StringIO

# AppEngine imports
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext import db
from google.appengine.api import images

# Local imports
import models
import EXIF
import fantasm

def goodDecode(encodedPayload):
    if not hasattr(encodedPayload, 'encoding'):
        return encodedPayload
    encoding = encodedPayload.encoding
    payload = encodedPayload.payload
    if encoding and encoding.lower() != '7bit':
        payload = payload.decode(encoding)
    return payload

def hasPhotoAttached(mail_message):
    if hasattr(mail_message,'attachments'):
        attachment_name = mail_message.attachments[0][0]
        logging.info('We have an attachment %s' % attachment_name)

        # We will only take a jpeg
        if attachment_name.endswith('.jpg', '.JPG', '.jpeg', '.JPEG'):
            return True

    return False

def getMailBody(mail_message):
    # Get the body text out of the email
    plaintext_bodies = mail_message.bodies('text/plain')
    body_text = ""
    for content_type, body in plaintext_bodies:
        body_text = body_text + body.decode() + " "
    return body_text


class DefaultMailHandler(InboundMailHandler):
    """Handle incoming mail from users """

    def receive(self, mail_message):
        """ process incoming messages from email accounts """
        logging.info("Received a message from: " + mail_message.sender)
        blacklisted = models.BlackList.get_blacklist_by_email(mail_message.sender)

        if blacklisted:
            blacklisted.counter += 1
            blacklisted.put()

        self.saveMessage(mail_message)

    def saveMessage(self, mail_message):
        """ Process all inbound mail messages from users """

        # Save the email as a message
        message = models.Message()

        message.sender = mail_message.sender
        message.to = mail_message.to
        if hasattr(mail_message, 'subject'):
            message.subject = mail_message.subject

        message.body = getMailBody(mail_message)

        if hasPhotoAttached(mail_message):

            # Get the image data from the first attachment
            image_data = goodDecode(mail_message.attachments[0][1])
            img = images.Image(image_data)
            image_data_length = len(image_data)
            logging.info("Attachment length " + str(image_data_length))

            # Save the photo if it will fit into a db.blob property
            if image_data_length < 1000000:
                message.picture = db.Blob(img)
            else:
                img.resize(width=600,height=600)
                message.picture = db.Blob(img.execute_transforms(output_encoding=images.JPEG))

            # Get the exif data from the photo
            tags = EXIF.process_file(StringIO(str(image_data)))
            message.exif_data = pickle.dumps(tags)

        message.put()

        fantasm.fsm.startStateMachine('ProcessMessage', [{'key': message.key()}])