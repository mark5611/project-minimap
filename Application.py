import threading
import time
from os.path import isfile
from pathlib import Path

from colorama import Fore

import math

from playsound3 import playsound

import CoreLogic
import OSMMapExtractor
import OfflineOSMManager
import DataBaseConnection
import runTime
import datetime
from datetime import datetime as dt

current_speed_limit = 0
current_road = None
success = 0
fail = 0

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
        OfflineOSMManager.OSMManager().download_manager("austria", "https://download.geofabrik.de/europe/austria.html")
        OSMMapExtractor.MyHandler().applicator()
        OSMMapExtractor.Decoder("austria").writeDecoded()

        with open("./misc_data/lastLogdate.txt", "w") as log:
            today = datetime.date.today()
            log.write(str(today))
def checkEmptyDb():
    conncetion = DataBaseConnection.DataBaseConnection()
    result = conncetion.Query("SELECT EMPTY_DATABASE FROM SETTINGS")

    if result[0][0] == 1 or result[0][0] == str("1"):
        OSMMapExtractor.MyHandler().applicator()
        OSMMapExtractor.Decoder("austria").writeDecoded()
        conncetion.Query("UPDATE SETTINGS SET EMPTY_DATABASE = 0")

def mainLoop():
    global success, fail
    while True:
        try:
            newApplication = CoreApplication(region="austria", sound_setting="male")
            newApplication.roadAndSpeedLimit()
            newApplication.checkSpeedCameras()
            del newApplication

            freq = float(runTime.calculate_update_times(success))
            if (freq - 1) <= 1:
                time.sleep(1)

            print(Fore.GREEN + f"\n--------------\nSuccess: {success}\nFail: {fail}\nUpdate frequency: {runTime.calculate_update_times(success)}\n--------------")

        except Exception as ex:
            print(ex)

class SessionHandler():
    def __init__(self):
        self.dbConn = DataBaseConnection.DataBaseConnection()
        self.latestId = None
        self.startTime = None
        self.endTime = None

    def getLatestId(self):
        self.latestId = self.dbConn.Query("SELECT SESSION FROM SESSIONS ORDER BY SESSION DESC LIMIT 1;")
        if self.latestId is None or self.latestId == []:
            self.latestId = 1
        else:
            self.latestId = self.latestId[0][0]+1

    def recordSessionStart(self):
        self.startTime = datetime.datetime.now()

    def recordSessionEnd(self):
        self.endTime = datetime.datetime.now()

    def execute(self):
        self.dbConn.Query(
            "INSERT INTO SESSIONS VALUES (?, ?, ?, ?, ?)",
            (self.latestId, self.startTime, self.endTime, success, fail)
        )

#TODO: finish the class
class DetectionHandler():
    def __init__(self):
        self.dbConn = DataBaseConnection.DataBaseConnection()
        self.latestId = None
        self.latestFk = None

    def getLatestIds(self):
        self.latestId = self.dbConn.Query("SELECT DETECTION_ID FROM DETECTIONS ORDER BY SESSION DESC LIMIT 1;")
        self.latestFk = self.dbConn.Query("SELECT SESSION FROM SESSIONS ORDER BY SESSION DESC LIMIT 1;")

    def execute(self):
        self.dbConn.Query("")

class CoreApplication():
    def __init__(self, region: str, sound_setting="male"):
        self.user_cords = CoreLogic.UserLocation().getUserLocation()
        self.dbConn = DataBaseConnection.DataBaseConnection()
        self.sound_setting = sound_setting
        self.user_lat = self.user_cords[0]
        self.user_lon = self.user_cords[1]
        self.tol = 10
        self.current_road = ""
        self.region = region

    def roadAndSpeedLimit(self):
        global current_speed_limit, current_road, success, fail

        tol = self.tol

        while True:
            matching_road = CoreLogic.Roads(self.user_cords, tol).speed_limits()

            if matching_road:
                success += 1
                print(Fore.CYAN + "\nUser Location" + Fore.RESET)
                current_road = matching_road[0][1]
                print(f"---------------\nstreet name: {current_road}")
                print(f"---------------\nspeed limit: {matching_road[0][2]}\n--------------\n")
                if current_speed_limit != matching_road[0][2]:
                    print(Fore.CYAN + "New Limit" + Fore.RESET)
                    current_speed_limit = matching_road[0][2]
                    if self.sound_setting == "male":
                        sound = "./sound_files/Male_voice/" + str(current_speed_limit) + ".mp3"
                        if isfile(sound):
                            playsound(sound)
                        else:
                            playsound("./sound_files/Male_voice/new-speed-limit.mp3")
                break

            else:
                fail += 1
                tol += 2
                print(Fore.RED + f"\nNew Tolerance: {tol}\nRetrying\n" + Fore.RESET)


    def checkSpeedCameras(self):
        cameras = CoreLogic.Cameras(self.user_cords).cameras()
        closest = None
        if cameras != [] and cameras != None:
            for c in cameras:
                cam_cord = [c[2], c[3]]   # DB row: (id, region, lat, lon)
                print(Fore.WHITE + "\nCalculating Distance" + Fore.RESET)
                distance = camera_distance_m(self.user_lat, self.user_lon, cam_cord[0], cam_cord[1])
                if closest is None:
                    closest = distance
                elif distance < closest:
                    closest = distance
            playsound("./sound_files/Male_voice/speed-cam.mp3")
            print(Fore.RED + f"\nSpeed Camera in: {int(closest)} meters" + Fore.RESET)
        else:
            print(Fore.WHITE + "\nNo Cameras in Area" + Fore.RESET)

checkRequiredDirectoryExists()
checkEmptyDb()
logLastOnDate()

newSession = SessionHandler()

newSession.getLatestId()
runtime_thread = threading.Thread(target=runTime.main, daemon=True)
runtime_thread.start()

newSession.recordSessionStart()

mainLoop()

newSession.recordSessionEnd()
newSession.execute()