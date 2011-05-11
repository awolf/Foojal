from datetime import datetime
from settings import COUNTRY_TIMEZONES

import unittest
import pytz

class TestTimezoneOptions(unittest.TestCase):
    def test_all_timezones_in_pytz_module(self):
        """ The default counter for a new blacklist should be 1"""
        for zone in COUNTRY_TIMEZONES:
            now = today = datetime.utcnow().replace(tzinfo=pytz.utc)

            timezone = pytz.timezone(zone['key'])

            date_at_timezone = now.astimezone(timezone)

            assert(date_at_timezone)
