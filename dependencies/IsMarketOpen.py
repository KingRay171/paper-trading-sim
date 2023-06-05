import datetime
from holidays.financial import ny_stock_exchange

us_holidays = ny_stock_exchange.NYSE()

def market_is_open(now=None) -> bool:
    """
    Checks if US equity markets are open. Uses the current time if no parameters are
    given, will use the date specified if a datetime object is passed in
    """
    if not now:
        now = datetime.datetime.now()

    # Current time is between 9:30 am and 4:00 pm
    open_time = datetime.time(hour=9, minute=30, second=0)
    close_time = datetime.time(hour=16, minute=0, second=0)

    # Check if the current time is a holiday
    if now.strftime('%Y-%m-%d') in us_holidays:
        return False
    # Check if the current time is within open and close time
    if (now.time()<open_time) or (now.time()>close_time):
        return False
    # Check if it's a weekday
    if now.date().weekday()>4:
        return False
    return True
