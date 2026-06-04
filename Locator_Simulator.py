import time

import ipinfo
from requests import get
import random

location = None
def getLocation():
    global location
    #one time API location call
    ip = get('https://api.ipify.org').content.decode('utf8')
    print(ip)

    access_token = '03efe6077df3f8'
    handler = ipinfo.getHandler(access_token)
    data = handler.getDetails(ip)
    location = (float(data.details['latitude']), float(data.details['longitude']))
    return location

directions = ["lat", "lon"]
def simulate_movement():
    global location
    c = random.choice(directions)
    movement = 0.002
    if c == "lat":
        location = (location[0]+movement, location[1])
    else:
        location = (location[0], location[1]+movement)

    time.sleep(1)
    return location

