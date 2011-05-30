from __future__ import with_statement
from google.appengine.api import files
from google.appengine.api.capabilities import CapabilitySet

from google.appengine.dist import use_library

use_library('django', '1.2')

# Python imports
import logging

# AppEngine imports
from django.http import HttpResponse
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.api import images

# Local imports
import models
import settings
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
    if hasattr(mail_message, 'attachments'):
        attachment_name = mail_message.attachments[0][0]
        logging.info('We have an attachment %s' % attachment_name)

        # We will only take a jpeg
        if attachment_name.endswith(settings.ALLOWED_IMAGE_EXTENSIONS):
            return True

    return False


def getMailBody(mail_message):
    # Get the body text out of the email
    plaintext_bodies = mail_message.bodies('text/plain')
    body_text = ""
    for content_type, body in plaintext_bodies:
        body_text = body_text + body.decode() + " "
    return body_text.strip()


class DefaultMailHandler(InboundMailHandler):
    """Handle incoming mail from users """

    def receive(self, mail_message):
        """ process incoming messages from email accounts """

        images_enabled = CapabilitySet('images').is_enabled()
        if not images_enabled:
            logging.info("Image capability not enabled" )
            return HttpResponse('Image capability not enabled', status=503)

        datastore_write_enabled = CapabilitySet('datastore_v3', capabilities=['write']).is_enabled()
        if not datastore_write_enabled:
            logging.info("Data store write capability not enabled" )
            return HttpResponse('Data store write capability not enabled', status=503)

        taskqueue_enabled = CapabilitySet('taskqueue').is_enabled()
        if not taskqueue_enabled:
            logging.info("task queue capability not enabled" )
            return HttpResponse('task queue capability not enabled', status=503)


        #    CapabilitySet('images').is_enabled()
        #if not CapabilitySet(['images', 'blobstore', 'taskqueue']).is_enabled():
        #    logging.info("Capability not enabled" )
        #    return HttpResponse('Capability not enabled', status=503)

        logging.info("Received a message from: " + mail_message.sender)

        self.saveMessage(mail_message)

    def saveMessage(self, mail_message):
        """ Process all inbound mail messages from users """

        # Save the email as a message
        message = models.Message()

        message.sender = mail_message.sender
        message.to = mail_message.to
        if hasattr(mail_message, 'subject'):
            message.subject = mail_message.subject.lower()

        message.body = getMailBody(mail_message)

        if hasPhotoAttached(mail_message):
            # Get the image data from the first attachment
            image_data = goodDecode(mail_message.attachments[0][1])
            image_data_length = len(image_data)
            logging.info("Attachment length " + str(image_data_length))

            #lets get the dimensions of the image while we have a chance
            img = images.Image(image_data)
            message.picture_height = img.height
            message.picture_width = img.width

            try:
                # Create the file
                file_name = files.blobstore.create(mime_type='image/jpeg')

                with files.open(file_name, 'a') as f:
                    for i in xrange(0, len(image_data), 1000000):
                        f.write(image_data[i:i + 1000000])

                # Finalize the file. Do this before attempting to read it.
                files.finalize(file_name)

                # Get the file's blob key
                blob_key = files.blobstore.get_blob_key(file_name)
                logging.info("New Image blob key is :" + str(blob_key))

                message.picture_key = str(blob_key)

                message.picture_url = images.get_serving_url(blob_key=str(blob_key))
                logging.info("New Image serving uri is :" + str(message.picture_url))

            except Exception, err:
                logging.info("Error saving blob " + str(err))
                return HttpResponse('Foojal: App Engine is undergoing maintenance. '
                                'Please try again in a while. ' + str(err),
                                status=503)

        message.put()

        fantasm.fsm.startStateMachine('ProcessMessage', [{'key': message.key()}])


class InvitesMailHandler(InboundMailHandler):
    """Handle incoming mail for invite mail account. """

    def receive(self, mail_message):
        logging.info("Invites mail handler received a message from: %s" % mail_message.sender)
        return

class SupportMailHandler(InboundMailHandler):
    """Handle incoming mail for invite mail account. """

    def receive(self, mail_message):
        logging.info("Support mail handler received a message from: %s" % mail_message.sender)
        return