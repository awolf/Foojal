from __future__ import with_statement

from google.appengine.api import files

""" Processing message actions """

from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext import db
from fantasm.action import FSMAction
from StringIO import StringIO

import EXIF
import models
import pickle
import settings

class FindMemeberStatus(FSMAction):
    def execute(self, context, obj):
        message = models.Message.get_by_id(context['key'].id())
        context['sender'] = message.sender
        account = models.Account.get_account_by_email(message.sender)

        if account:
            if account.is_expired:
                return 'expired'
            else:
                message.owner = account.user
                message.put()
                return 'member'
        else:
            return 'invite'


class InviteMemeber(FSMAction):
    def execute(self, context, obj):
        models.Invitation.send_invitation(context['sender'])
        return 'success'


class ExpiredMemeber(FSMAction):
    def execute(self, context, obj):
        message = models.Message.get_by_id(context['key'].id())
        account = models.Account.get_by_id(message.owner)

        # todo: we should email the user to pay up motherfucker
        if account:
            if account.is_expired:
                if account.should_blacklist:
                    return 'blacklist'
        pass


class BlacklistMemeber(FSMAction):
    def execute(self, context, obj):
        message = models.Message.get_by_id(context['key'].id())
        models.BlackList.blacklist_email(message.sender)
        pass


class PrepareEntry(FSMAction):
    def execute(self, context, obj):
        message = models.Message.get_by_id(context['key'].id())

        entry = models.Entry()
        entry.owner = message.owner
        entry.sender = message.sender
        entry.picture_url = message.picture_url
        entry.put()

        context['entrykey'] = entry.key()

        if message.picture_key:
            return 'hasphoto'
        else:
            return 'nophoto'


class GetExifTags(FSMAction):
    def execute(self, context, obj):
        message = models.Message.get_by_id(context['key'].id())

        blob_reader = blobstore.BlobReader(message.picture_key, buffer_size=5000)
        tags = EXIF.process_file(StringIO(str(blob_reader.read())))

        if tags:
            try:
                entry = models.Entry.get_by_id(context['entrykey'].id())
                entry.exif_data = pickle.dumps(tags)
                entry.put()

                context['orientation'] = str(tags["Image Orientation"])
                context['longitude'] = tags['GPS GPSLongitude']
                context['longitudeReference'] = str(tags['GPS GPSLongitudeRef'])
                context['latitude'] = tags['GPS GPSLatitude']
                context['latitudeReference'] = str(tags['GPS GPSLatitudeRef'])
            except Exception, err:
                context.logger.info("Error fetching GPS Tags " + str(err))

        else:
            pass

        return 'success'


class CreatePhoto(FSMAction):
    def execute(self, context, obj):
        if settings.DEBUG: return 'success'

        message = models.Message.get_by_id(context['key'].id())

        img = images.Image(blob_key=message.picture_key)

        if context.has_key('orientation'):
            orientation = context['orientation']
            degrees = 0

            if orientation == "Rotated 90 CW":
                degrees = 90
            elif orientation == "Rotated 180":
                degrees = 180
            elif orientation == "Rotated 90 CCW":
                degrees = 270

            if degrees:
                context.logger.info("image rotated %s degrees" % degrees)
                img.rotate(degrees)

        if message.picture_width > 1600 or message.picture_height > 1600:
            if message.picture_width > message.picture_height:
                img.resize(width=1600)
            else:
                img.resize(height=1600)

        img.im_feeling_lucky()

        rotated_image = img.execute_transforms(output_encoding=images.JPEG)

        file_name = files.blobstore.create(mime_type='image/jpeg')

        with files.open(file_name, 'a') as f:
            f.write(rotated_image)

        files.finalize(file_name)
        blob_key = files.blobstore.get_blob_key(file_name)
        
        entry = models.Entry.get_by_id(context['entrykey'].id())
        entry.picture_url = images.get_serving_url(blob_key=str(blob_key))
        entry.picture_key = str(blob_key)
        entry.put()

        blobstore.delete(message.picture_key)
        
        return 'success'


class GeocodeImage(FSMAction):
    def execute(self, context, obj):
        if context.has_key('longitude') and context.has_key('latitude'):
            longitude = context['longitude'].decode()
            longitude = str(longitude)[1:-1].split(',')
            longitudeCoordinate = models.GetGeoPt(longitude, str(context['longitudeReference']))

            latitude = context['latitude'].decode()
            latitude = str(latitude)[1:-1].split(',')
            latitudeCoordinate = models.GetGeoPt(latitude, str(context['latitudeReference']))

            if latitudeCoordinate is None or longitudeCoordinate is None:
                return 'success'
            entry = models.Entry.get_by_id(context['entrykey'].id())
            entry.location = db.GeoPt(latitudeCoordinate, longitudeCoordinate)
            entry.put()

        return 'success'


class ProcessTags(FSMAction):
    def execute(self, context, obj):
        message = models.Message.get_by_id(context['key'].id())
        entry = models.Entry.get_by_id(context['entrykey'].id())
        if message.subject:
            entry.tags = [tag for tag in message.subject.split(' ') if tag]
            entry.put()
        return 'complete'


class ProcessContent(FSMAction):
    def execute(self, context, obj):
        message = models.Message.get_by_id(context['key'].id())
        entry = models.Entry.get_by_id(context['entrykey'].id())
        if message.body:
            content = message.body.replace("Sent from my iPhone", "")
            entry.content = content
        entry.put()

        return 'complete'


class CleanUpMessage(FSMAction):
    def execute(self, context, obj):
        message = models.Message.get_by_id(context['key'].id())
        message.delete()
        pass
