import osmium
import json

def main():
    filepath_hu = "./osm-data/hungary.osm.pbf"
    filepath_at = "./osm-data/austria.osm.pbf"

    def writeDecoded(countryname):
        with open(f"./decoded_data/{countryname}_roads.json", "w", encoding="utf-8") as f:
            json.dump(json_roads, f, ensure_ascii=False, indent=4)

        with open(f"./decoded_data/{countryname}_cams.json", "w", encoding="utf-8") as f:
            json.dump(json_cams, f, ensure_ascii=False, indent=4)

    class MyHandler(osmium.SimpleHandler):
        def __init__(self):
            super().__init__()

            # NEW: count processed OSM objects
            self.processed_items = 0

            # NEW: print progress every N objects
            self.progress_step = 10000

        # NEW: helper for simple progress reporting without knowing total size
        def update_progress(self):
            self.processed_items += 1

            # NEW: print every 10,000 processed objects
            if self.processed_items % self.progress_step == 0:
                print(f"\rProgress: ~{self.processed_items} elements", end="", flush=True)

        def way(self, w):
            # NEW: update progress for each way seen
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
            # NEW: update progress for each node seen
            self.update_progress()

            if n.tags.get("highway") == "speed_camera":
                json_cams.append({"lat": n.lat, "lon": n.lon})

    json_roads = []
    json_cams = []
    handler1 = MyHandler()
    handler1.apply_file(filepath_hu, locations=True)
    writeDecoded("hungary")
    #
    json_roads = []
    json_cams = []
    handler2 = MyHandler()
    handler2.apply_file(filepath_at, locations=True)
    writeDecoded("austria")



