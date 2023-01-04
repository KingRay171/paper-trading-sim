import datetime, holidays

us_holidays = holidays.US()

# The method automatically uses the current time but a specific time can be inserted into the method as a parameter.
def isMarketOpen(now=None):
        if not now:
            now = datetime.datetime.now()
        
        # Current time is between 9:30 am and 4:00 pm
        openTime = datetime.time(hour=9, minute=30, second=0)
        closeTime = datetime.time(hour=16, minute=0, second=0)
  
        # Check if the current time is a holiday
        if now.strftime('%Y-%m-%d') in us_holidays:
            return False

        # Check if the current time is within open and close time 
        if (now.time()<openTime) or (now.time()>closeTime):
            return False

        # Check if it's a weekday
        if now.date().weekday()>4:
            return False

        return True
