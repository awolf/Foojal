#import foo.models
#import os
#import sys
#import unittest
#import time
#from google.appengine.api import users
#from google.appengine.api import urlfetch
#from google.appengine.api import apiproxy_stub_map
#from google.appengine.api import urlfetch_stub
#from google.appengine.api import user_service_stub
#
#
#class TestBlackList(unittest.TestCase):
#
#  def test_add_blacklist(self):
#    """
#    Add A users email to the blacklist."""
#
#    blacklist = foo.models.BlackList(email='test@test.com', counter=1)
#    self.assertEqual(blacklist.email, 'test@test.com')
#    self.assertNotEqual(blacklist.counter, 0)
##
##    # Get the added quotes by creation order
##    quotes, next = models.get_quotes_newest()
##    self.assertEqual(quotes[0].key().id(), quoteid2)
##    self.assertEqual(models.get_quote(quoteid2).key().id(), quoteid2)
##
##    self.assertEqual(len(quotes), 2)
##
##    # Remove one quote
##    models.del_quote(quoteid2, user)
##
##    quotes, next = models.get_quotes_newest()
##    self.assertEqual(quotes[0].key().id(), quoteid)
##    self.assertEqual(len(quotes), 1)
##
##
##    # Remove last remaining quote
##    models.del_quote(quoteid, user)
##    quotes, next = models.get_quotes_newest()
##    self.assertEqual(len(quotes), 0)
## """
#
##if __name__ == '__main__':
##    unittest.main()
#
