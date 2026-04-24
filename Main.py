import json
from math import cos

import requests

import Locator

cords = Locator.get_current_location()
lat, lon = cords["latitude"], cords["longitude"]
lat5, lon5 = lat+0.0045, lon+(0.0045 / cos(lat))
lat_n5, lon_n5 = lat-0.0045, lon-(0.0045 / cos(lat))
print(lat, lon)

query = f"""
[out:json][timeout:90][bbox:{lon_n5},{lat_n5},{lon5},{lat5}];
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

speed_limits = []
cameras = []

for el in data.get("elements", []):
    tags = el.get("tags", {})

    if el["type"] == "way" and "maxspeed" in tags:
        speed_limits.append({
            "id": el["id"],
            "name": tags.get("name"),
            "maxspeed": tags.get("maxspeed"),
            "geometry": el.get("geometry", []),
        })

    elif el["type"] == "node" and tags.get("highway") == "speed_camera":
        cameras.append({
            "id": el["id"],
            "lat": el.get("lat"),
            "lon": el.get("lon"),
            "maxspeed": tags.get("maxspeed"),
            "direction": tags.get("direction"),
        })

with open("speed_limits.json", "w", encoding="utf-8") as f:
    json.dump(speed_limits, f, ensure_ascii=False, indent=2)

with open("cameras.json", "w", encoding="utf-8") as f:
    json.dump(cameras, f, ensure_ascii=False, indent=2)