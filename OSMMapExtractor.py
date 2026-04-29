import osmium
import json
from pathlib import Path

json_roads = []
json_cams = []

class MyHandler(osmium.SimpleHandler):
    def __init__(self, targetCountry = "./osm-data/austria.osm.pbf"):
        super().__init__()

        self.targetCountry = targetCountry

        '''filepath_hu = "./osm-data/hungary.osm.pbf"
        filepath_at = "./osm-data/austria.osm.pbf"'''


        self.processed_items = 0

        self.progress_step = 10000

    def update_progress(self):
        self.processed_items += 1

        if self.processed_items % self.progress_step == 0:
            print(f"\rProgress: ~{self.processed_items} elements", end="", flush=True)

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

class Decoder():
    def __init__(self, countryName):
        self.countryName = countryName

    def writeDecoded(self):
        print("writing")
        Path("./decoded_data").mkdir(parents=True, exist_ok=True)
        with open(f"./decoded_data/{self.countryName}_roads.json", "w", encoding="utf-8") as f:
            json.dump(json_roads, f, ensure_ascii=False)

        with open(f"./decoded_data/{self.countryName}_cams.json", "w", encoding="utf-8") as f:
            json.dump(json_cams, f, ensure_ascii=False)
