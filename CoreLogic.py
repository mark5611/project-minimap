from math import cos, radians

import json
from colorama import Fore

import Locator
#
camera_detection_range = 1000

def getUserLocation():
    userCords = Locator.get_current_location()
    lat, lon = userCords["latitude"], userCords["longitude"]
    return(lat, lon)

def getRoads(region):
    with open(f"./decoded_data/{region}_roads.json", "r") as file:
        decoded_data = json.load(file)
        return decoded_data

def getCameras(region):
    with open(f"./decoded_data/{region}_cams.json", "r") as file:
        decoded_data = json.load(file)
        return decoded_data

def speed_limits(region):
    try:
        print(Fore.WHITE + "\nLocating User" + Fore.RESET)
        coords = getUserLocation()
        lat, lon = coords[0], coords[1]

        lat_offset = 50 / 111320
        lon_offset = 50 / (111320 * cos(radians(lat)))

        south = lat - lat_offset
        west = lon - lon_offset
        north = lat + lat_offset
        east = lon + lon_offset

        roads = []

        for road in getRoads(region):
            for pt in road["coords"]:
                pt_lat = pt["lat"]
                pt_lon = pt["lon"]

                if south <= pt_lat <= north and west <= pt_lon <= east:
                    roads.append(road)
                    break

        return roads

    except Exception as e:
        print(e)

def cameras(region):
    try:
        print(Fore.WHITE + "\nLocating User" + Fore.RESET)
        coords = getUserLocation()
        lat, lon = coords[0], coords[1]

        lat_offset = camera_detection_range / 111320
        lon_offset = camera_detection_range / (111320 * cos(radians(lat)))

        south = lat - lat_offset
        west = lon - lon_offset
        north = lat + lat_offset
        east = lon + lon_offset

        cameras = []

        for cam in getCameras(region):
            pt_lat = cam["lat"]
            pt_lon = cam["lon"]

            if south <= pt_lat <= north and west <= pt_lon <= east:
                cameras.append(cam)
                break

        return cameras

    except Exception as e:
        print(e)

print(getUserLocation())