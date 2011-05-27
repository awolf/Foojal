from calendar import monthrange
from time import strftime
import unittest
from foo.date_helper import week_begin_end_dates, get_day_data, get_week_data, get_month_data
from datetime import date, datetime, timedelta
from foo.models import Account
from google.appengine.ext import testbed
import pytz

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


class TestDateHelpersTimeSpans(unittest.TestCase):
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


class TestDayDateHelpers(unittest.TestCase):
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

    def test_day_in_the_past(self):
        day = date(2011, 2, 22)
        values = get_day_data(self.account, day)

        from_date = datetime(hour=0, minute=0, day=day.day, year=day.year, month=day.month).replace(
            tzinfo=self.account.tz)
        to_date = datetime(hour=23, minute=59, second=59, day=day.day, year=day.year, month=day.month).replace(
            tzinfo=self.account.tz)

        assert from_date == values['from_date']
        assert to_date == values['to_date']
        assert from_date == values['target_day']
        assert from_date == values['display_date']
        assert values['previous_date_url'] == "/day/21/02/2011"
        assert values['next_date_url'] == "/day/23/02/2011"

    def test_today(self):
        """ Test that getting the current day will
        return the correct dates including a
        none for the next day """

        today = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(self.account.tz)
        day = datetime(hour=18, minute=0, day=today.day, year=today.year, month=today.month).replace(tzinfo=self.account.tz)
        yesterday = day - timedelta(days=1)
        
        from_date = datetime(hour=0, minute=0, day=day.day, year=day.year, month=day.month).replace(
            tzinfo=self.account.tz)
        to_date = datetime(hour=23, minute=59, second=59, day=day.day, year=day.year, month=day.month).replace(
            tzinfo=self.account.tz)

        values = get_day_data(self.account, day)

        assert from_date == values['from_date']
        assert to_date == values['to_date']
        assert from_date == values['target_day']
        assert from_date == values['display_date']
        assert values['previous_date_url'] == strftime("/day/%d/%m/%Y", yesterday.timetuple())
        assert values['next_date_url'] is None


class TestWeekDateHelpers(unittest.TestCase):
    """ Testing the week helpers in
    the date helpers module."""

    account = None

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.account = Account(timezone='America/Phoenix')

    def tearDown(self):
        self.testbed.deactivate()

    def test_week_in_the_past(self):
        values = get_week_data(self.account, "8", "2011")

        from_date = datetime(hour=0, minute=0, day=21, year=2011, month=2).replace(tzinfo=self.account.tz)
        to_date = datetime(hour=23, minute=59, day=27, year=2011, month=2).replace(tzinfo=self.account.tz)

        assert from_date == values['from_date']
        assert to_date == values['to_date']
        assert from_date == values['target_day']
        assert from_date == values['display_date']
        assert values['previous_date_url'] == "/week/07/2011"
        assert values['next_date_url'] == "/week/09/2011"

    def test_today(self):
        calendar = datetime.utcnow().isocalendar()
        week = calendar[1]
        year = calendar[0]
        week_begin, week_end = week_begin_end_dates(week, year)

        values = get_week_data(self.account, week, year)

        from_date = datetime(hour=0, minute=0, day=week_begin.day, year=week_begin.year,
                             month=week_begin.month).replace(tzinfo=self.account.tz)
        to_date = datetime(hour=23, minute=59, day=week_end.day, year=week_end.year, month=week_end.month).replace(
            tzinfo=self.account.tz)

        previous_date_url = "/week/" + str(week - 1) + "/2011"

        assert from_date == values['from_date']
        assert to_date == values['to_date']
        assert from_date == values['target_day']
        assert from_date == values['display_date']
        assert values['previous_date_url'] == previous_date_url
        assert values['next_date_url'] is None


class TestMonthDateHelpers(unittest.TestCase):
    """ Testing the month helpers in
    the date helpers module."""

    account = None

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.account = Account(timezone='America/Phoenix')

    def tearDown(self):
        self.testbed.deactivate()

    def test_month_in_the_past(self):
        values = get_month_data(self.account, "1", "2011")

        from_date = datetime(hour=0, minute=0, day=1, year=2011, month=1).replace(tzinfo=self.account.tz)
        to_date = datetime(hour=23, minute=59, day=31, year=2011, month=1).replace(tzinfo=self.account.tz)

        assert from_date == values['from_date']
        assert to_date == values['to_date']
        assert from_date == values['target_day']
        assert from_date == values['display_date']
        assert values['previous_date_url'] == "/month/12/2010"
        assert values['next_date_url'] == "/month/02/2011"

    def test_today(self):
        today = datetime.date(datetime.now())
        month = today.month
        year = today.year

        values = get_month_data(self.account, month, year)
        days_in_month = monthrange(int(year), int(month))[1]

        from_date = datetime(hour=0, minute=0, day=1, year=int(year), month=int(month)).replace(tzinfo=self.account.tz)

        to_date = datetime(hour=23, minute=59, day=days_in_month, year=int(year), month=int(month)).replace(
            tzinfo=self.account.tz)

        a_day = timedelta(days=1)

        previous_date = from_date - a_day
        previous_date_url = strftime("/month/%m/%Y", previous_date.timetuple())

        assert from_date == values['from_date']
        assert to_date == values['to_date']
        assert from_date == values['target_day']
        assert from_date == values['display_date']
        assert values['previous_date_url'] == previous_date_url
        assert values['next_date_url'] is None
