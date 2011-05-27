from calendar import monthrange
from time import strftime
from datetime import datetime, timedelta, date
import pytz

def week_begin_end_dates(week, year):
    d = date(year, 1, 1)
    delta_days = d.isoweekday() - 1
    delta_weeks = week
    if year == d.isocalendar()[0]:
        delta_weeks -= 1
        # delta for the beginning of the week
    delta = timedelta(days=-delta_days, weeks=delta_weeks)
    beginning = d + delta
    # delta2 for the end of the week
    delta2 = timedelta(days=6 - delta_days, weeks=delta_weeks)
    end = d + delta2
    return beginning, end


def get_day_data(account, date):
    today = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(account.tz).replace(tzinfo=account.tz)
    from_date = datetime(hour=0, minute=0, day=date.day, year=date.year, month=date.month).replace(
        tzinfo=account.tz)

    to_date = datetime(hour=23, minute=59, second=59, day=date.day, year=date.year, month=date.month).replace(
        tzinfo=account.tz)

    previous_date = from_date - timedelta(days=1)
    previous_date_url = strftime("/day/%d/%m/%Y", previous_date.timetuple())

    next_date = from_date + timedelta(days=1)
    if next_date >= today:
        next_date_url = None
    else:
        next_date_url = strftime("/day/%d/%m/%Y", next_date.timetuple())

    values = {
        "from_date": from_date,
        "to_date": to_date,
        "heading": strftime("%A %B %d ", from_date.timetuple()),
        "target_day": from_date,
        "display_date": from_date,
        "previous_date_url": previous_date_url,
        "next_date_url": next_date_url
    }
    return values


def get_week_data(account, week, year):
    today = datetime.utcnow().replace(tzinfo=account.tz).date()
    beginning_date, end_date = week_begin_end_dates(int(week), int(year))

    from_date = datetime(hour=0, minute=0, day=beginning_date.day, year=beginning_date.year,
                         month=beginning_date.month).replace(tzinfo=account.tz)
    to_date = datetime(hour=23, minute=59, day=end_date.day, year=end_date.year, month=end_date.month).replace(
        tzinfo=account.tz)

    previous_week = beginning_date - timedelta(days=1)
    previous_date_url = strftime("/week/%W/%Y", previous_week.timetuple())

    next_week = end_date + timedelta(days=1)
    if end_date > today:
        next_date_url = None
    else:
        next_date_url = strftime("/week/%W/%Y", next_week.timetuple())

    values = {
        "from_date": from_date,
        "to_date": to_date,
        "heading": "The %s week of %s" % (week, year),
        "target_day": from_date,
        "display_date": from_date,
        "previous_date_url": previous_date_url,
        "next_date_url": next_date_url
    }
    return values


def get_month_data(account, month, year):
    today = datetime.utcnow().replace(tzinfo=account.tz)
    days_in_month = monthrange(int(year), int(month))[1]

    from_date = datetime(hour=0, minute=0, day=1, year=int(year), month=int(month)).replace(tzinfo=account.tz)

    to_date = datetime(hour=23, minute=59, day=days_in_month, year=int(year), month=int(month)).replace(
        tzinfo=account.tz)

    a_day = timedelta(days=1)

    previous_date = from_date - a_day
    previous_date_url = strftime("/month/%m/%Y", previous_date.timetuple())

    next_date = to_date + a_day

    if next_date >= today:
        next_date_url = None
    else:
        next_date_url = strftime("/month/%m/%Y", next_date.timetuple())

    values = {
        "from_date": from_date,
        "to_date": to_date,
        "heading": strftime("%B %Y ", from_date.timetuple()),
        "target_day": from_date,
        "display_date": from_date,
        "previous_date_url": previous_date_url,
        "next_date_url": next_date_url
    }
    return values