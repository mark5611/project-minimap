import threading
from colorama import Fore

import math
import Locator
import Main
import runTime

runtime_thread = threading.Thread(target=runTime.main, daemon=True)
runtime_thread.start()

current_road = ""
current_speed_limit = 0

coords = Locator.get_current_location()
lat, lon = coords["latitude"], coords["longitude"]

def roadAndSpeedLimit():
    global current_speed_limit, current_road



    speed_limits = Main.speed_limits()
    lim = speed_limits

    target_lat = lat
    target_lon = lon
    tol = 0.0001

    while tol <= 0.0002:
        match = next(
            (
                elem
                for elem in lim
                if any(
                abs(point["lat"] - target_lat) <= tol and
                abs(point["lon"] - target_lon) <= tol
                for point in elem.get("geometry", [])
            )
            ),
            None
        )

        if match:
            print(f"\n---------------\nstreet name: {match.get("name")}")
            print(f"---------------\nspeed limit: {match.get("maxspeed")}\n--------------\n")
            if current_speed_limit != match.get("maxspeed"):
                print(Fore.CYAN + "New Limit" + Fore.RESET)
                current_speed_limit = match.get("maxspeed")
                # sound
            break

        elif not match and tol < 0.0002:
            tol += 0.0001
        else:
            print(Fore.RED + "\nUnable to Locate" + Fore.RESET)
            break

def camera_distance_m(user_lat, user_lon, cam_lat, cam_lon):
    R = 6371000  # meters

    phi1 = math.radians(user_lat)
    phi2 = math.radians(cam_lat)
    dphi = math.radians(cam_lat - user_lat)
    dlambda = math.radians(cam_lon - user_lon)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def checkSpeedCameras():
    cameras = Main.cameras()
    closest = None
    if cameras != [] and cameras != None:
        for c in cameras:
            cam_cord=[c["lat"], c["lon"]]
            distance = camera_distance_m(48.2250,16.3950, cam_cord[0], cam_cord[1])
            if closest == None:
                closest = distance
            elif distance < closest:
                closest = distance
        print(Fore.RED+f"\nSpeed Camera in: {int(closest)} meters"+Fore.RESET)

while True:
    try:
        roadAndSpeedLimit()
        checkSpeedCameras()

    except Exception as ex:
        print(ex)

