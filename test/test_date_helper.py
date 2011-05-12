import unittest
from foo.date_helper import week_begin_end_dates, get_day_data, get_week_data, get_month_data
from datetime import date
from foo.models import Account
from google.appengine.ext import testbed

class TestWeekDatesHelper(unittest.TestCase):
    """ Testing the week begin and end
    helpers in the date helper module."""

    def test_week_begins_on_monday(self):
        """ Weeks begin dates should be a monday."""
        beginning, end = week_begin_end_dates(1, 2011)
        assert(beginning.weekday() == 0)

    def test_week_ends_on_sunday(self):
        """ Week end dates should be a sunday."""
        beginning, end = week_begin_end_dates(1, 2011)
        assert(end.weekday() == 6)

    def test_first_monday_2011(self):
        """ The first Monday of 2011 is 1/3/2011."""
        beginning, end = week_begin_end_dates(1, 2011)
        assert(beginning == date(2011, 1, 3))

    def test_first_sunday_2011(self):
        """ The first Sunday of 2011 is 1/9/2011."""
        beginning, end = week_begin_end_dates(1, 2011)
        assert(end == date(2011, 1, 9))

    def test_last_monday_2011(self):
        """ The last monday of 2011 is 12/26/2011."""
        beginning, end = week_begin_end_dates(52, 2011)
        assert(beginning == date(2011, 12, 26))

    def test_last_sunday_2011(self):
        """ The last Sunday of 2011 is 1/1/2012."""
        beginning, end = week_begin_end_dates(52, 2011)
        assert(end == date(2012, 1, 1))


class TestDateHelpersTimeDeltas(unittest.TestCase):
    """ Testing the single day helpers in
    the date helpers module."""

    account = None

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.account = Account(timezone='America/Phoenix')

    def tearDown(self):
        self.testbed.deactivate()

    def test_single_day_is_24_hours(self):
        values = get_day_data(self.account, date(2011, 1, 1))

        td = values['to_date'] - values['from_date']
        days, hours, minutes = td.days, td.seconds // 3600, td.seconds // 60 % 60

        assert(days == 0)
        assert(hours == 23)
        assert(minutes == 59)

    def test_single_week_is_7_days(self):
        values = get_week_data(self.account, 1, 2011)

        td = values['to_date'] - values['from_date']
        days, hours, minutes = td.days, td.seconds // 3600, td.seconds // 60 % 60

        assert(days == 6)
        assert(hours == 23)
        assert(minutes == 59)

    def test_first_month_of_2011_is_31_days(self):
        values = get_month_data(self.account, 1, 2011)

        td = values['to_date'] - values['from_date']
        days, hours, minutes = td.days, td.seconds // 3600, td.seconds // 60 % 60

        assert(days == 30)
        assert(hours == 23)
        assert(minutes == 59)
