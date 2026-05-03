from math import cos, radians

from colorama import Fore

import DataBaseConnection
import Locator_macOS

camera_detection_range = 800

class UserLocation():
    def __init__(self, locator_preference = "macOS"):
        self.locator_preference = locator_preference
        self.location = Locator_macOS.get_current_location()
        print(print(Fore.RED + "\n------\nUpdating Location\n--------\n" + Fore.RESET))

    def getUserLocation(self):
        lat, lon = self.location["latitude"], self.location["longitude"]
        return(lat, lon)

class Roads():
    def __init__(self, targetLocation, tol=10):
        self.targetLocation = targetLocation
        self.tol = tol
        self.dbConn = DataBaseConnection.DataBaseConnection()

    def speed_limits(self):
        try:
            coords = self.targetLocation
            lat, lon = coords[0], coords[1]

            lat_offset = self.tol / 111320
            lon_offset = self.tol / (111320 * cos(radians(lat)))

            south = lat - lat_offset
            west = lon - lon_offset
            north = lat + lat_offset
            east = lon + lon_offset

            matching_road = self.dbConn.Query(
                """SELECT ROAD.* FROM ROAD 
                JOIN ROAD_COORDS ON ROAD.ROAD_ID = ROAD_COORDS.ROAD_ID 
                WHERE ROAD_COORDS.LAT BETWEEN ? AND ? 
                AND ROAD_COORDS.LON BETWEEN ? AND ?""",
                (south, north, west, east)
            )

            return matching_road

        except Exception as e:
            print(e)

class Cameras():
    def __init__(self, targetLocation):
        self.targetLocation = targetLocation
        self.dbConn = DataBaseConnection.DataBaseConnection()

    def cameras(self):
        try:
            coords = self.targetLocation
            lat, lon = coords[0], coords[1]

            lat_offset = camera_detection_range / 111320
            lon_offset = camera_detection_range / (111320 * cos(radians(lat)))

            south = lat - lat_offset
            west = lon - lon_offset
            north = lat + lat_offset
            east = lon + lon_offset

            cameras = self.dbConn.Query(
                "SELECT * FROM SPEED_CAMERA WHERE LAT BETWEEN ? AND ? AND LON BETWEEN ? AND ?",
                (south, north, west, east)
            )

            '''
                        for cam in getCameras(region):
                pt_lat = cam["lat"]
                pt_lon = cam["lon"]

                if south <= pt_lat <= north and west <= pt_lon <= east:
                    cameras.append(cam)
            '''


            return cameras

        except Exception as e:
            print(e)

