import pause
from datetime import datetime
from datetime import timedelta
import os

def round_to_next_hour(date):
    date += timedelta(seconds=60-date.second)
    date += timedelta(minutes=60-date.minute)
    #new_date = date + timedelta(minutes=60-date.minute)
    return date

def time_str(date):
    return '{:%H:%M:%S %d/%m/%Y}'.format(date)

date = datetime.now()
print('Current time is ' + time_str(date))

failure_limit = 3
dir = os.path.dirname(os.path.realpath(__file__))

while True:
    date = round_to_next_hour(date)
    print('Next run is at ' + time_str(date))
    dt = datetime(date.year, date.month, date.day, date.hour, date.minute, date.second, 0).timestamp()
    pause.until(dt)
    fails = 0
    while fails < 3 and os.system('python ' + dir + '\gotmoon.py') != 0:
        fails += 1
    if fails == 3:
        print('Program failed 3 times at ' + time_str(date))
        break

