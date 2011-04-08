#!/usr/bin/env python
from google.appengine.dist import use_library
import fantasm

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

        # TODO: Need to check the capabilities API to see if data store is up and running

        self.saveMessage(mail_message)
        self.saveAttachment(mail_message)

    def saveMessage(self, mail_message):
        """ Process all inbound mail messages from users """

        logging.info("Received a message from: " + mail_message.sender)

        # Save the email as a message
        message = models.Message()

        message.sender = mail_message.sender
        message.to = mail_message.to
        if hasattr(mail_message, 'subject'):
            message.subject = mail_message.subject

         # Get the body text out of the email
        plaintext_bodies = mail_message.bodies('text/plain')
        body_text = ""
        for content_type, body in plaintext_bodies:
            body_text = body_text + body.decode() + " "
        message.body = str(body_text)

        message.put()

        fantasm.fsm.startStateMachine('ProcessMessage', [{'key': message.key()}])

    def saveAttachment(self, mail_message):
        # Save the attachment as a Photo

        if hasattr(mail_message,'attachments'):
            
            attachment_name = mail_message.attachments[0][0]

            # We will only take a jpeg
            if attachment_name.endswith('.jpg', '.JPG', '.jpeg', '.JPEG'):
                logging.info('We have an attachment %s' % attachment_name)
                photo = models.Photo()
                photo.sender = db.Email(mail_message.sender)
                
                # Get the image data from the first attachment
                image_data = goodDecode(mail_message.attachments[0][1])
                img = images.Image(image_data)
                image_data_length = len(image_data)
                logging.info("Attachment length " + str(image_data_length))

                # Save the photo if it will fit into a db.blob property
                if image_data_length < 1000000:
                    photo.picture = db.Blob(img)
                else:
                    img.resize(width=600,height=600)
                    photo.picture = db.Blob(img.execute_transforms(output_encoding=images.JPEG))

                # Get the exif data from the photo
                tags = EXIF.process_file(StringIO(str(image_data)))
                photo.exif_data = pickle.dumps(tags)

                photo.put()

                fantasm.fsm.startStateMachine('ProcessPhoto', [{'key': photo.key()}])
