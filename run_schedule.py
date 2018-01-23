import pause
from datetime import datetime
from datetime import timedelta

def round_to_next_hour(date):
    new_date = date + timedelta(seconds=60-date.second, minutes=60-date.second)
    #new_date = date + timedelta(minutes=60-date.minute)
    return new_date

def time_str(date):
    return '{:%H:%M:%S %d/%m/%Y}'.format(date)

date = datetime.now()
print('Current time is ' + time_str(date))

date = round_to_next_hour(date)
print('Next run is at ' + time_str(date))

#while True:
#    pause.until(datetime())