from math import cos, radians

import requests
import Locator


def cameras():
    try:
        coords = Locator.get_current_location()
        lat, lon = coords["latitude"], coords["longitude"]

        lat_offset = 500 / 111320
        lon_offset = 500 / (111320 * cos(radians(lat)))

        south = lat - lat_offset
        west = lon - lon_offset
        north = lat + lat_offset
        east = lon + lon_offset

        #print(f"\nbbox = {south},{west},{north},{east}")

        query = f"""
        [out:json][timeout:90][bbox:{south},{west},{north},{east}];
        (
          way[highway][maxspeed];
          node[highway=speed_camera];
        );
        out body geom;
        """

        resp = requests.post(
            "https://overpass.private.coffee/api/interpreter",
            data={"data": query},
            headers={"Accept": "application/json"},
            timeout=90,
        )
        resp.raise_for_status()
        data = resp.json()

       # print("\nelements:", len(data.get("elements", [])))

        cameras = []

        for el in data.get("elements", []):
            tags = el.get("tags", {})

            if el["type"] == "node" and tags.get("highway") == "speed_camera":
                cameras.append({
                    "id": el["id"],
                    "lat": el.get("lat"),
                    "lon": el.get("lon"),
                    "maxspeed": tags.get("maxspeed"),
                    "direction": tags.get("direction"),
                })
        return cameras

        '''with open("speed_limits.json", "w", encoding="utf-8") as f:
            json.dump(speed_limits, f, ensure_ascii=False, indent=2)
    
        with open("cameras.json", "w", encoding="utf-8") as f:
            json.dump(cameras, f, ensure_ascii=False, indent=2)
    
        print("\nspeed limits:", len(speed_limits))
        print("cameras:", len(cameras))'''
    except Exception as e:
        print(e)

def speed_limits():
    try:
        coords = Locator.get_current_location()
        lat, lon = coords["latitude"], coords["longitude"]

        lat_offset = 50 / 111320
        lon_offset = 50 / (111320 * cos(radians(lat)))

        south = lat - lat_offset
        west = lon - lon_offset
        north = lat + lat_offset
        east = lon + lon_offset

        #print(f"\nbbox = {south},{west},{north},{east}")

        query = f"""
        [out:json][timeout:90][bbox:{south},{west},{north},{east}];
        (
          way[highway][maxspeed];
          node[highway=speed_camera];
        );
        out body geom;
        """

        resp = requests.post(
            "https://overpass.private.coffee/api/interpreter",
            data={"data": query},
            headers={"Accept": "application/json"},
            timeout=90,
        )
        resp.raise_for_status()
        data = resp.json()

       # print("\nelements:", len(data.get("elements", [])))

        speed_limits = []

        for el in data.get("elements", []):
            tags = el.get("tags", {})

            if el["type"] == "way" and "maxspeed" in tags:
                speed_limits.append({
                    "id": el["id"],
                    "name": tags.get("name"),
                    "maxspeed": tags.get("maxspeed"),
                    "geometry": el.get("geometry", []),
                })
        return speed_limits

        '''with open("speed_limits.json", "w", encoding="utf-8") as f:
            json.dump(speed_limits, f, ensure_ascii=False, indent=2)
    
        with open("cameras.json", "w", encoding="utf-8") as f:
            json.dump(cameras, f, ensure_ascii=False, indent=2)
    
        print("\nspeed limits:", len(speed_limits))
        print("cameras:", len(cameras))'''
    except Exception as e:
        print(e)