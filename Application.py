import threading
from colorama import Fore

import Locator
import Main
import runTime

runtime_thread = threading.Thread(target=runTime.main, daemon=True)
runtime_thread.start()

current_road = ""
current_speed_limit = 0

while True:
    try:
        coords = Locator.get_current_location()
        lat, lon = coords["latitude"], coords["longitude"]

        speed_limits = Main.speed_limits()
        lim = speed_limits
        lim_geo = [elem.get("geometry") for elem in lim]
        lim_geo = [elem for elem in lim_geo]
        lim_name = [elem.get("name") for elem in lim]

        target_lat = lat
        target_lon = lon
        tol = 0.0001


        while tol <= 0.0002:
            match = next(
                (
                    elem
                    for elem in lim
                    if any(
                    abs(point["lat"] - target_lat) <= tol and
                    abs(point["lon"] - target_lon) <= tol
                    for point in elem.get("geometry", [])
                )
                ),
                None
            )

            if match:
                print(f"\n---------------\nstreet name: {match.get("name")}")
                print(f"---------------\nspeed limit: {match.get("maxspeed")}\n--------------\n")
                if current_speed_limit != match.get("maxspeed"):
                    print(Fore.CYAN+"New Limit"+Fore.RESET)
                    current_speed_limit = match.get("maxspeed")
                    #sound
                break

            elif not match and tol <= 0.0002:
                tol += 0.0001
            else:
                print(Fore.RED+"\nUnable to Locate"+Fore.RESET)
                break


    except Exception as ex:
        print(ex)

