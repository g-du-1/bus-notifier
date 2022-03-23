
#!/usr/bin/python3

import requests
import datetime
import math
from bs4 import BeautifulSoup
from time import sleep
from numpy import random

dt = datetime.datetime

bus_stop_link = "http://www.rslpublic.co.uk/mobiledepboard/WYPTEDefaultMenu.aspx?id=45024729&cid=595&RTI=True"

# bus_stop_link = "http://www.rslpublic.co.uk/mobiledepboard/WYPTEDefaultMenu.aspx?id=45022032&cid=595&RTI=True"

notification_time = 10

previous_service = ""
notified = False

# TODO When the form is empty soup will be nonetype. Deal with this edge case

while True:

    # Throttle the requests for random amount of seconds between two values
    sleep(random.uniform(31, 49))

    bus_stop_data = requests.get(bus_stop_link)
    bus_stop_soup = BeautifulSoup(bus_stop_data.text, features="html.parser")

    closest_bus_service = bus_stop_soup.find(id="depsList_ctl00_lblService").text
    closest_bus_dest = bus_stop_soup.find(id="depsList_ctl00_lblDestination").text
    closest_bus_time = bus_stop_soup.find(id="depsList_ctl00_lblTime").text

    # Time can be ie 5 min or ie 14:50 for buses with no live data
    if " min" in closest_bus_time:
        closest_bus_rem_mins = closest_bus_time.replace(" min", "")
        closest_bus_rem_mins = int(closest_bus_rem_mins)
    else:
        hours_int = int(closest_bus_time.split(':')[0])
        mins_int = int(closest_bus_time.split(':')[1])
        now = dt.now()

        bustime_object = dt(year=now.year, month=now.month, day=now.day, hour=hours_int, minute=mins_int)
        difference = bustime_object - now
        closest_bus_rem_mins = math.ceil(difference.seconds / 60)

        notif_msg = closest_bus_service + " " + closest_bus_dest + " " + closest_bus_time
    if closest_bus_service != previous_service:
        notified = False
        previous_service = closest_bus_service
    if (closest_bus_rem_mins <= notification_time) and not notified:
        requests.post('slack webook url', json={'text': 'slack message {}'.format(notif_msg)})
        notified = True
        print("Notification sent!")
    print(closest_bus_service + " " + closest_bus_dest + " " + closest_bus_time)
