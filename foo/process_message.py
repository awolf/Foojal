""" Processing message actions """

from google.appengine.api import images
from google.appengine.ext import db
from fantasm.action import FSMAction

import models
import pickle

class FindMemeberStatus(FSMAction):
    def execute(self, context, obj):
        context.logger.info('IsMemeber.execute()')
        context.logger.info("Process message key := %s" % (str(context['key'])))
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
        context.logger.info('InviteMemeber.execute()')
        context.logger.info("Queueing invitation to %s" % (context['sender']))

        models.Invitation.send_invitation(context['sender'])
        return 'success'

class ExpiredMemeber(FSMAction):
    def execute(self, context, obj):
        context.logger.info('ExpiredMemeber.execute()')
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
        context.logger.info('BlacklistMemeber.execute()')
        message = models.Message.get_by_id(context['key'].id())
        models.BlackList.blacklist_email(message.sender)
        pass


class PrepareEntry(FSMAction):
    def execute(self, context, obj):
        context.logger.info('PrepareEntry.execute()')
        message = models.Message.get_by_id(context['key'].id())

        entry = models.Entry()
        entry.owner = message.owner
        entry.sender = message.sender
        entry.exif_data = message.exif_data
        entry.put()

        context['entrykey'] = entry.key()

        if message.picture:
            return 'hasphoto'
        else:
            return 'nophoto'

class GetExifTags(FSMAction):
    def execute(self, context, obj):
        context.logger.info('GetExifTags.execute()')
        message = models.Message.get_by_id(context['key'].id())

        if message.exif_data:
            try:
                tags = pickle.loads(message.exif_data)
                context['orientation'] = str(tags["Image Orientation"])
                #context.logger.info(str(tags["Image Orientation"]))

                context['longitude'] = tags['GPS GPSLongitude']
                #context.logger.info(str(tags['GPS GPSLongitude']))

                context['longitudeReference'] = str(tags['GPS GPSLongitudeRef'])
                #context.logger.info(str(tags['GPS GPSLongitudeRef']))

                context['latitude'] = tags['GPS GPSLatitude']
                #context.logger.info(str(tags['GPS GPSLatitude']))

                context['latitudeReference'] = str(tags['GPS GPSLatitudeRef'])
                #context.logger.info(str(tags['GPS GPSLatitudeRef']))
            except Exception, err:
                context.logger.info("Error fetching GPS Tags " + str(err))
            else:
                pass
            
        return 'success'

class CreatePhoto(FSMAction):
    def execute(self, context, obj):
        context.logger.info('CreatePhoto.execute()')

        message = models.Message.get_by_id(context['key'].id())

        if context.has_key('orientation'):
            orientation = context['orientation']

            img = images.Image(message.picture)
            img.resize(width=600,height=600)

            if orientation == "Rotated 90 CW":
                img.rotate(90)
                context.logger.info('image rotated 90')
            elif orientation == "Rotated 180":
                img.rotate(180)
                context.logger.info('image rotated 180')
            elif orientation == "Rotated 90 CCW":
                img.rotate(270)
                context.logger.info('image rotated 260')

            img.im_feeling_lucky()
            photo = models.Photo()
            photo.owner = message.owner
            photo.picture = db.Blob(img.execute_transforms(output_encoding=images.JPEG))
            photo.put()

            entry = models.Entry.get_by_id(context['entrykey'].id())
            entry.picture_uid = str(photo.key().id())
            entry.put()

        return 'success'

class CreateThumbnail(FSMAction):
    def execute(self, context, obj):
        context.logger.info('CreateThumbnail.execute()')

        message = models.Message.get_by_id(context['key'].id())

        img = images.Image(message.picture)
        img.resize(width=48,height=48)

        photo = models.Photo()
        photo.owner = message.owner
        photo.picture = db.Blob(img.execute_transforms(output_encoding=images.JPEG))
        photo.put()

        entry = models.Entry.get_by_id(context['entrykey'].id())
        entry.thumbnail_uid = str(photo.key().id())
        entry.put()
        
        return 'success'

class GeocodeImage(FSMAction):
    def execute(self, context, obj):
        context.logger.info('GeocodeImage.execute()')

        if context.has_key('longitude') and context.has_key('latitude'):

            longitude = context['longitude'].decode()
            longitude = str(longitude)[1:-1].split(',')
            longitudeCoordinate = models.GetGeoPt(longitude,str(context['longitudeReference']))

            latitude = context['latitude'].decode()
            latitude = str(latitude)[1:-1].split(',')
            latitudeCoordinate = models.GetGeoPt(latitude,str(context['latitudeReference']))

            entry = models.Entry.get_by_id(context['entrykey'].id())
            entry.location = db.GeoPt(latitudeCoordinate, longitudeCoordinate)
            entry.put()

        return 'success'

class ProcessTags(FSMAction):
    def execute(self, context, obj):
        context.logger.info('ProcessTags.execute()')
        message = models.Message.get_by_id(context['key'].id())
        entry = models.Entry.get_by_id(context['entrykey'].id())
        entry.tags = message.subject.split(' ')
        entry.put()
        return 'complete'

class ProcessContent(FSMAction):
    def execute(self, context, obj):
        context.logger.info('ProcessContent.execute()')

        message = models.Message.get_by_id(context['key'].id())
        entry = models.Entry.get_by_id(context['entrykey'].id())
        entry.content = message.body
        entry.put()

        return 'complete'

class CleanUpMessage(FSMAction):
    def execute(self, context, obj):
        context.logger.info('CleanUpMessage.execute()')

        message = models.Message.get_by_id(context['key'].id())
        message.delete()
        pass
