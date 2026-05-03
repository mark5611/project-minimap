import threading
import time
from os.path import isfile
from pathlib import Path

from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QFont, QColor, QPixmap, QIcon
from colorama import Fore

import math

from playsound3 import playsound

from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, \
    QStackedLayout
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
app_status = None
isSpeedCamera = False

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
    global success, fail, app_status
    while True:
        try:
            newApplication = CoreApplication(region="austria", sound_setting="male")
            app_status = "Fetching Location..."
            newApplication.roadAndSpeedLimit()
            app_status = "Locating Road..."
            newApplication.checkSpeedCameras()
            app_status = "Checking Speed Cameras..."
            del newApplication

            print(Fore.GREEN + f"\n--------------\nSuccess: {success}\nFail: {fail}\nUpdate frequency: {runTime.calculate_update_times(success)}\n--------------")

        except Exception as ex:
            print(ex)
def main():
    loop_thread = threading.Thread(target=mainLoop, daemon=True)
    loop_thread.start()

    GUI().start()
class GUI():
    def __init__(self):
        self.app = QApplication([])
        self.window = QWidget()

    def start(self):
        self.window.setGeometry(0, 0, 480, 320)

        main_layout = QVBoxLayout()
        self.window.setLayout(main_layout)

        road_container = QWidget()
        road_container.setFixedSize(300, 70)

        stacked_r = QStackedLayout(road_container)
        stacked_r.setStackingMode(QStackedLayout.StackAll)

        road_label = QLabel(str(current_road))
        road_label.setFont(QFont("Helvetica", 30, QFont.Bold))
        road_label.setStyleSheet("color: black;")
        main_layout.addWidget(road_label)
        road_label.setAlignment(Qt.AlignCenter)

        road_sign = QLabel()
        road_sign.setPixmap(QPixmap("./Icons/roadName.png").scaled(300, 70, Qt.KeepAspectRatio))
        road_sign.setAttribute(Qt.WA_TransparentForMouseEvents)
        road_sign.setStyleSheet("background: transparent;")

        stacked_r.addWidget(road_label)
        stacked_r.addWidget(road_sign)

        main_layout.addWidget(road_container)

        limit_container = QWidget()
        limit_container.setFixedSize(70, 70)

        stacked = QStackedLayout(limit_container)
        stacked.setStackingMode(QStackedLayout.StackAll)

        limit_label = QLabel(str(current_speed_limit))
        limit_label.setFont(QFont("Helvetica", 25, QFont.Bold))
        limit_label.setStyleSheet("color: black;")
        limit_label.setAlignment(Qt.AlignCenter)

        sign_label = QLabel()
        sign_label.setPixmap(QPixmap("./Icons/SpeedLimitSign.png").scaled(70, 70, Qt.KeepAspectRatio))
        sign_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        sign_label.setStyleSheet("background: transparent;")

        stacked.addWidget(limit_label)
        stacked.addWidget(sign_label)

        row = QHBoxLayout()
        row.addSpacing(80)
        row.addWidget(limit_container)
        row.addStretch()
        main_layout.addLayout(row)

        speed_cam = QLabel()
        speed_cam.setPixmap(QPixmap("./Icons/no_speed_cam.png").scaled(70, 70, Qt.KeepAspectRatio))

        row = QHBoxLayout()
        row.addSpacing(80)
        row.addWidget(limit_container)
        row.addSpacing(30)  # gap between the two icons
        row.addWidget(speed_cam)
        row.addStretch()
        main_layout.addLayout(row)

        main_layout.addStretch()

        status_label = QLabel("Current Status: " + str(app_status))
        status_label.setFont(QFont("Helvetica", 15))
        status_label.setStyleSheet("color: lightblue;")
        status_label.setAlignment(Qt.AlignBottom)

        quit_btn = QPushButton()
        quit_btn.setIcon(QIcon("./Icons/powerOff.png"))
        quit_btn.setIconSize(QSize(50, 50))
        quit_btn.setStyleSheet("background: transparent; border: none;")
        quit_btn.clicked.connect(self.window.close)

        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignBottom)
        btn_row.addWidget(status_label)
        btn_row.addStretch()
        btn_row.addWidget(quit_btn)
        main_layout.addLayout(btn_row)

        update_frequency = QLabel("Update Frequency: " + str(runTime.calculate_update_times(success)))
        update_frequency.setFont(QFont("Helvetica", 15))
        update_frequency.setStyleSheet("color: lightblue;")

        main_layout.addWidget(update_frequency)

        def update_labels():
            status_label.setText("Current Status: "+str(app_status))
            road_label.setText(str(current_road))
            limit_label.setText(str(current_speed_limit))
            update_frequency.setText("Update Frequency: " + str(runTime.calculate_update_times(success)))
            if not isSpeedCamera:
                speed_cam.setPixmap(QPixmap("./Icons/no_speed_cam.png").scaled(70, 70, Qt.KeepAspectRatio))
            else:
                speed_cam.setPixmap(QPixmap("./Icons/speed_cam.png").scaled(70, 70, Qt.KeepAspectRatio))

        timer = QTimer()
        timer.timeout.connect(update_labels)
        timer.start(800)

        self.window.show()
        self.app.exec()

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
        global isSpeedCamera
        cameras = CoreLogic.Cameras(self.user_cords).cameras()
        closest = None
        if cameras != [] and cameras != None:
            isSpeedCamera = True
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
            isSpeedCamera = False
            print(Fore.WHITE + "\nNo Cameras in Area" + Fore.RESET)

checkRequiredDirectoryExists()
checkEmptyDb()
logLastOnDate()

newSession = SessionHandler()

newSession.getLatestId()
runtime_thread = threading.Thread(target=runTime.main, daemon=True)
runtime_thread.start()

newSession.recordSessionStart()

main()

newSession.recordSessionEnd()
newSession.execute()