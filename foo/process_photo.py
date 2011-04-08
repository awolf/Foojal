""" Processing Photo actions """

from google.appengine.api import images
from google.appengine.ext import db
from fantasm.action import FSMAction

import models
import pickle

class AssignOwnership(FSMAction):
    def execute(self, context, obj):
        context.logger.info('AssignOwnership.execute()')
        photo = models.Photo.get_by_id(context['key'].id())

        account = models.Account.get_account_by_email(photo.sender)
        if account:
            photo.owner = account.key()
            photo.put()
            return 'hasowner'

        pass

class GetExifTags(FSMAction):
    def execute(self, context, obj):
        context.logger.info('RotateImage.execute()')
        photo = models.Photo.get_by_id(context['key'].id())

        tags = pickle.loads(photo.exif_data)
        context['orientation'] = str(tags["Image Orientation"])
        context['longitude'] = str(tags['GPS GPSLongitude'])
        context['longitudeReference'] = str(tags['GPS GPSLongitudeRef'])
        context['latitude'] = str(tags['GPS GPSLatitude'])
        context['latitudeReference'] = str(tags['GPS GPSLatitudeRef'])

        return 'success'
        

class RotateImage(FSMAction):
    def execute(self, context, obj):
        context.logger.info('RotateImage.execute()')
        photo = models.Photo.get_by_id(context['key'].id())

        orientation = context['orientation']

        img = images.Image(photo.picture)
        img.resize(width=600,height=600)

        if orientation == "Rotated 90 CW":
            img.rotate(90)
            context.logger.info("image rotated 90%")
        elif orientation == "Rotated 180":
            img.rotate(180)
            context.logger.info("image rotated 180%")
        elif orientation == "Rotated 90 CCW":
            img.rotate(270)
            context.logger.info("image rotated 260%")

        img.im_feeling_lucky()
        photo.picture = db.Blob(img.execute_transforms(output_encoding=images.JPEG))
        photo.put()

        return 'success'

class ThumbnailImage(FSMAction):
    def execute(self, context, obj):
        context.logger.info('ThumbnailImage.execute()')
        photo = models.Photo.get_by_id(context['key'].id())
        img = images.Image(photo.picture)
        img.resize(width=48,height=48)
        photo.thumbnail = db.Blob(img.execute_transforms(output_encoding=images.JPEG))
        photo.put()

        return 'success'

class GeocodeImage(FSMAction):
    def execute(self, context, obj):
        context.logger.info('GeocodeImage.execute()')
        photo = models.Photo.get_by_id(context['key'].id())
        
        if context['longitude'] is None or context['longitudeReference'] is None:
            return
        longitudeCoordinate = models.GetGeoPt(context['longitude'],context['longitudeReference'])

        if context['latitude'] is None or context['latitudeReference'] is None:
            return
        latitudeCoordinate = models.GetGeoPt(context['latitude'],context['latitudeReference'])

        photo.location = db.GeoPt(latitudeCoordinate, longitudeCoordinate)
        photo.put()

        pass