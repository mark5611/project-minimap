import threading
from pathlib import Path

from colorama import Fore

import math
import CoreLogic
import OSMMapExtractor
import OfflineOSMManager
import runTime
import datetime
from datetime import datetime as dt

current_road = ""
current_speed_limit = 0

located = False
coords = CoreLogic.getUserLocation()
user_lat, user_lon = coords[0], coords[1]

success, fail = 0,0

def roadAndSpeedLimit(region):
    global current_speed_limit, current_road, success, fail

    speed_limits = CoreLogic.speed_limits(region)
    lim = speed_limits

    target_lat = user_lat
    target_lon = user_lon
    tol = 0.0001

    if speed_limits != [] and speed_limits != None:
        while not located:
            match = next(
                (
                    elem
                    for elem in lim
                    if any(
                    abs(point["lat"] - target_lat) <= tol and
                    abs(point["lon"] - target_lon) <= tol
                    for point in elem.get("coords", [])
                )
                ),
                None
            )

            if match:
                success += 1
                print(Fore.CYAN+"\nUser Location"+Fore.RESET)
                print(f"---------------\nstreet name: {match.get("roadName")}")
                print(f"---------------\nspeed limit: {match.get("maxspeed")}\n--------------\n")
                if current_speed_limit != match.get("maxspeed"):
                    print(Fore.CYAN + "New Limit" + Fore.RESET)
                    current_speed_limit = match.get("maxspeed")
                    # sound
                break

            else:
                fail += 1
                tol += 0.0001
                print(Fore.RED+f"\nNew Tolerance: {tol}\nRetrying\n"+Fore.RESET)
        else:
            fail += 1
            roadAndSpeedLimit("austria")
    else:
        print(Fore.BLUE + "\nRetrying..." + Fore.RESET)
        roadAndSpeedLimit("austria")

def camera_distance_m(user_lat, user_lon, cam_lat, cam_lon):
    print(Fore.WHITE+"\nCalculating Distance"+Fore.RESET)
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

def checkSpeedCameras(region):
    cameras = CoreLogic.cameras(region)
    closest = None
    if cameras != [] and cameras != None:
        for c in cameras:
            cam_cord=[c["lat"], c["lon"]]
            distance = camera_distance_m(user_lat,user_lon, cam_cord[0], cam_cord[1])
            if closest == None:
                closest = distance
            elif distance < closest:
                closest = distance
        print(Fore.RED+f"\nSpeed Camera in: {int(closest)} meters"+Fore.RESET)
    else:
        print(Fore.WHITE+"\nNo Cameras in Area"+Fore.RESET)

def logLastOnDate():
    last_update_window = None
    with open("./misc_data/lastLogdate.txt", "r") as logr:
        last_update_window = logr.readline()


    with open("./misc_data/lastLogdate.txt", "w") as log:
        today = datetime.date.today()
        last_update_date =dt.strptime(last_update_window, "%Y-%m-%d").date()

        if (today - datetime.timedelta(days = 25)) >=  last_update_date:
            choice = input("\nIt is recommended to update the dataset. Proceed? (Y/N) ")

            if choice == "Y" or choice == "y":

                OfflineOSMManager.download_manager("hungary", "https://download.geofabrik.de/europe/hungary.html")
                OfflineOSMManager.download_manager("austria", "https://download.geofabrik.de/europe/austria.html")

                OSMMapExtractor.main()
                log.write(str(today))
            else:
                print("\nNext reminder: Next launch")
                log.write(last_update_window)
        else:
            print("\nDataset Up To Date")
            log.write(last_update_window)

def checkRequiredDirectoryExists():
    required_directory1 = Path("./decoded_data")
    required_directory2 = Path("./osm-data")

    if not required_directory1.exists() or not required_directory2.exists():

        print(Fore.RED+"Missing Dataset Detected......\nDownloading\n"+Fore.RESET)
        OfflineOSMManager.download_manager("hungary", "https://download.geofabrik.de/europe/hungary.html")
        OfflineOSMManager.download_manager("austria", "https://download.geofabrik.de/europe/austria.html")

        OSMMapExtractor.main()

        with open("./misc_data/lastLogdate.txt", "w") as log:
            today = datetime.date.today()
            log.write(str(today))


checkRequiredDirectoryExists()
logLastOnDate()

runtime_thread = threading.Thread(target=runTime.main, daemon=True)
runtime_thread.start()

while True:
    try:
        roadAndSpeedLimit("austria")
        checkSpeedCameras("austria")

        print(Fore.GREEN+f"\n--------------\nSuccess: {success}\nFail: {fail}\nUpdate frequency: {runTime.calculate_update_times(success)}\n--------------")


    except Exception as ex:
        print(ex)

