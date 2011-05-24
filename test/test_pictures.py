import unittest
import fixtures
import foo
from foo.models import GetGeoPt
import foo.EXIF

class TestGeoPoint(unittest.TestCase):
    def testLatLong(self):
        test_cases = fixtures.test_cases
        for test in test_cases:
            if test['has_geo']:
                path = '/Users/awolf/Desktop/home/test/images/' + test['file_name']
                tags = foo.EXIF.process_file(open(path, 'r'))

                longitudeExif = str(tags['GPS GPSLongitude'])
                longitude = longitudeExif.decode()
                longitude = str(longitude)[1:-1].split(',')
                longitudeReference = str(tags['GPS GPSLongitudeRef'])

                latitudeExif = str(tags['GPS GPSLatitude'])
                latitude = latitudeExif.decode()
                latitude = str(latitude)[1:-1].split(',')
                latitudeReference = str(tags['GPS GPSLatitudeRef'])

                log = GetGeoPt(longitude, longitudeReference)
                lat = GetGeoPt(latitude, latitudeReference)

                assert log
                assert lat

                print "The file %s has lat long of %s %s" % (path, str(lat), str(log))


class TestExifExtract(unittest.TestCase):

    def testExifExtraction(self):
        test_cases = fixtures.test_cases
        for test in test_cases:
            path = '/Users/awolf/Desktop/home/test/images/' + test['file_name']
            print "Testing EXIF extract " + test['file_name']
            tags = foo.EXIF.process_file(open(path, 'r'))
            assert tags


    def testPictureWithZerosForLatandLong(self):
        """ The image LG Lotus has a geo
        coordinates as zeros for lat and long
        """

        path = '/Users/awolf/Desktop/home/test/images/' + 'LG Lotus.jpeg'
        tags = foo.EXIF.process_file(open(path, 'r'))

        longitudeExif = str(tags['GPS GPSLongitude'])
        longitude = longitudeExif.decode()
        longitude = str(longitude)[1:-1].split(',')
        longitudeReference = str(tags['GPS GPSLongitudeRef'])

        latitudeExif = str(tags['GPS GPSLatitude'])
        latitude = latitudeExif.decode()
        latitude = str(latitude)[1:-1].split(',')
        latitudeReference = str(tags['GPS GPSLatitudeRef'])

        log = GetGeoPt(longitude, longitudeReference)
        lat = GetGeoPt(latitude, latitudeReference)

        self.assertFalse(log)
        self.assertFalse(lat)
