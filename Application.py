import threading
from os.path import isfile
from pathlib import Path

from colorama import Fore

import math

from playsound3 import playsound

import CoreLogic
import OSMMapExtractor
import OfflineOSMManager
import runTime
import datetime
from datetime import datetime as dt


def camera_distance_m(user_lat: float, user_lon: float, cam_lat: float, cam_lon: float) -> float:
    R = 6_371_000  # Earth's radius in metres

    phi1 = math.radians(user_lat)
    phi2 = math.radians(cam_lat)
    d_phi = math.radians(cam_lat - user_lat)
    d_lam = math.radians(cam_lon - user_lon)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lam / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

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

                OfflineOSMManager.OSMManager().download_manager("austria", "https://download.geofabrik.de/europe/austria.html")
                OSMMapExtractor.MyHandler().applicator()
                OSMMapExtractor.Decoder("austria").writeDecoded()

                #OfflineOSMManager.download_manager("hungary", "https://download.geofabrik.de/europe/hungary.html")
                #OfflineOSMManager.download_manager("austria", "https://download.geofabrik.de/europe/austria.html")

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
        #OfflineOSMManager.download_manager("hungary", "https://download.geofabrik.de/europe/hungary.html")
        #OfflineOSMManager.download_manager("austria", "https://download.geofabrik.de/europe/austria.html")
        OfflineOSMManager.OSMManager().download_manager("austria", "https://download.geofabrik.de/europe/austria.html")
        OSMMapExtractor.MyHandler().applicator()
        OSMMapExtractor.Decoder("austria").writeDecoded()

        with open("./misc_data/lastLogdate.txt", "w") as log:
            today = datetime.date.today()
            log.write(str(today))

class CoreApplication():
    def __init__(self, region: str, sound_setting="male"):
        self.sound_setting = sound_setting
        self.user_lat = CoreLogic.UserLocation().getUserLocation()[0]
        self.user_lon = CoreLogic.UserLocation().getUserLocation()[1]
        self.tol = 0.0001
        self.success = 0
        self.fail = 0
        self.current_road = ""
        self.current_speed_limit = 0
        self.region = region

    def roadAndSpeedLimit(self):
        speed_limits = CoreLogic.Roads().speed_limits(self.region)
        lim = speed_limits

        tol = 0.0001

        if speed_limits != [] and speed_limits != None:
            while True:
                match = next(
                    (
                        elem
                        for elem in lim
                        if any(
                        abs(point["lat"] - self.user_lat) <= tol and
                        abs(point["lon"] - self.user_lon) <= tol
                        for point in elem.get("coords", [])
                    )
                    ),
                    None
                )

                if match:
                    self.success += 1
                    print(Fore.CYAN + "\nUser Location" + Fore.RESET)
                    self.current_road = match.get("roadName")
                    print(f"---------------\nstreet name: {self.current_road}")
                    print(f"---------------\nspeed limit: {match.get("maxspeed")}\n--------------\n")
                    if self.current_speed_limit != match.get("maxspeed"):
                        print(Fore.CYAN + "New Limit" + Fore.RESET)
                        current_speed_limit = match.get("maxspeed")
                        if self.sound_setting == "male":
                            sound = "./sound_files/Male_voice/" + current_speed_limit + ".mp3"
                            if isfile(sound):
                                playsound(sound)
                            else:
                                playsound("./sound_files/Male_voice/new-speed-limit.mp3")
                    break

                else:
                    self.fail += 1
                    tol += 0.0001
                    print(Fore.RED + f"\nNew Tolerance: {tol}\nRetrying\n" + Fore.RESET)
        else:
            print(Fore.BLUE + "\nRetrying..." + Fore.RESET)
            self.roadAndSpeedLimit()

    def checkSpeedCameras(self):
        cameras = CoreLogic.Cameras().cameras(self.region)
        closest = None
        if cameras != [] and cameras != None:
            for c in cameras:
                cam_cord = [c["lat"], c["lon"]]
                print(Fore.WHITE + "\nCalculating Distance" + Fore.RESET)
                distance = camera_distance_m(self.user_lat, self.user_lon, cam_cord[0], cam_cord[1])
                if closest == None:
                    closest = distance
                elif distance < closest:
                    closest = distance
            playsound("./sound_files/Male_voice/speed-cam.mp3")
            print(Fore.RED + f"\nSpeed Camera in: {int(closest)} meters" + Fore.RESET)
        else:
            print(Fore.WHITE + "\nNo Cameras in Area" + Fore.RESET)


checkRequiredDirectoryExists()
logLastOnDate()

runtime_thread = threading.Thread(target=runTime.main, daemon=True)
runtime_thread.start()

newApplication = CoreApplication(region="austria", sound_setting="male")

while True:
    try:
        newApplication.roadAndSpeedLimit()
        newApplication.checkSpeedCameras()

        print(Fore.GREEN+f"\n--------------\nSuccess: {newApplication.success}\nFail: {newApplication.fail}\nUpdate frequency: {runTime.calculate_update_times(newApplication.success)}\n--------------")


    except Exception as ex:
        print(ex)

