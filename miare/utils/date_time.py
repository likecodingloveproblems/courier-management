import datetime

SATURDAY = 5


def get_yesterday_date():
    return datetime.date.today() - datetime.timedelta(days=1)


def get_this_and_past_saturday():
    this_saturday = datetime.date.today()
    past_saturday = this_saturday - datetime.timedelta(days=7)
    return this_saturday, past_saturday


def get_five_minutes_ago():
    return datetime.datetime.now() - datetime.timedelta(minutes=5)
