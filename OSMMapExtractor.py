import time

import osmium
import json
from pathlib import Path

import CoreLogic
import DataBaseConnection

json_roads = []
json_cams = []

class MyHandler(osmium.SimpleHandler):
    def __init__(self, targetCountry = "./osm-data/austria.osm.pbf"):
        super().__init__()

        self.targetCountry = targetCountry

        '''filepath_hu = "./osm-data/hungary.osm.pbf"
        filepath_at = "./osm-data/austria.osm.pbf"'''


        self.processed_items = 0

        self.progress_step = 1000

    def update_progress(self):
        self.processed_items += 1

        if self.processed_items % self.progress_step == 0:
            print(f"\rProcessing OSM Data.", end="", flush=True)
            time.sleep(0.1)
            print(f"\rProcessing OSM Data..", end="", flush=True)
            time.sleep(0.1)
            print(f"\rProcessing OSM Data...", end="", flush=True)
            time.sleep(0.1)

    def way(self, w):
        self.update_progress()

        if "highway" in w.tags and "maxspeed" in w.tags:
            roadName = w.tags.get("name", "Unnamed")
            maxSpeed = w.tags["maxspeed"]

            coords = []
            for node in w.nodes:
                if node.location.valid():
                    coords.append({
                        "lat": node.lat,
                        "lon": node.lon
                    })

            json_roads.append({
                "roadName": roadName,
                "maxspeed": maxSpeed,
                "coords": coords
            })

    def node(self, n):
        self.update_progress()

        if n.tags.get("highway") == "speed_camera":
            json_cams.append({"lat": n.lat, "lon": n.lon})

    def applicator(self):
        handler1 = MyHandler("austria")
        handler1.apply_file(self.targetCountry, locations=True)

class RoadsHandler():
    def __init__(self, region):
        self.dbConn = DataBaseConnection.DataBaseConnection()
        self.region = region
        self.roads = json_roads
        self.length = len(self.roads)
        self.roadId = 0
        self.coordId = 0
        self.roadName = None
        self.maxSpeed = None

    def parseRoads(self):
        for road in self.roads:
            self.roadId += 1
            self.roadName = road["roadName"]
            self.maxSpeed = road["maxspeed"]
            self.executeIntoRoads()
            coords = road["coords"]
            for coord in coords:
                self.coordId += 1
                lat = coord["lat"]
                lon = coord["lon"]
                self.executeIntoRoadCoords(lat, lon)

            print(f"\rProgress: {(self.roadId/self.length)*100:.2f}%", end="", flush=True)


    def executeIntoRoads(self):
        self.dbConn.Query("INSERT INTO ROAD VALUES (?,?,?,?)", (self.roadId, self.roadName, self.maxSpeed, self.region))

    def executeIntoRoadCoords(self, lat, lon):
        self.dbConn.Query("INSERT INTO ROAD_COORDS VALUES(?,?,?,?)", (self.coordId, self.roadId, lat, lon))

class SpeedCameraHandler():
    def __init__(self, region):
        self.dbConn = DataBaseConnection.DataBaseConnection()
        self.cameraId = 0
        self.region = region
        self.cams = json_cams
        self.length = len(json_cams)

    def parseCams(self):
        for cam in self.cams:
            self.cameraId += 1
            lat = cam["lat"]
            lon = cam["lon"]
            self.execute(lat, lon)
            print(f"\rProgress: {(self.cameraId / self.length) * 100:.2f}%", end="", flush=True)


    def execute(self, lat, lon):
        self.dbConn.Query("INSERT INTO SPEED_CAMERA VALUES(?,?,?,?)", (self.cameraId, self.region, lat, lon))



class Decoder():
    def __init__(self, countryName):
        self.countryName = countryName

    def writeDecoded(self):
        RoadsHandler(self.countryName).parseRoads()
        SpeedCameraHandler(self.countryName).parseCams()

        '''
        Path("./decoded_data").mkdir(parents=True, exist_ok=True)
        with open(f"./decoded_data/{self.countryName}_roads.json", "w", encoding="utf-8") as f:
            json.dump(json_roads, f, ensure_ascii=False)

        with open(f"./decoded_data/{self.countryName}_cams.json", "w", encoding="utf-8") as f:
            json.dump(json_cams, f, ensure_ascii=False)
'''