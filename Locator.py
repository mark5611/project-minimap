import sys
from Foundation import NSObject
from objc import super
from PyObjCTools import AppHelper
import CoreLocation


class LocationDelegate(NSObject):
    def init(self):
        self = super().init()
        if self is None:
            return None
        self.location = None
        self.error = None

        return self

    def locationManager_didUpdateLocations_(self, manager, locations):
        if locations and len(locations) > 0:
            loc = locations[-1]
            coord = loc.coordinate()
            self.location = {
                "latitude": coord.latitude,
                "longitude": coord.longitude,
                "accuracy_m": loc.horizontalAccuracy(),
            }
            manager.stopUpdatingLocation()
            AppHelper.stopEventLoop()

    def locationManager_didFailWithError_(self, manager, error):
        self.error = str(error)
        manager.stopUpdatingLocation()
        AppHelper.stopEventLoop()


def get_current_location():
    if not CoreLocation.CLLocationManager.locationServicesEnabled():
        raise RuntimeError("Location services are disabled.")

    manager = CoreLocation.CLLocationManager.alloc().init()
    delegate = LocationDelegate.alloc().init()
    manager.setDelegate_(delegate)

    if hasattr(manager, "requestWhenInUseAuthorization"):
        manager.requestWhenInUseAuthorization()

    manager.startUpdatingLocation()
    AppHelper.runConsoleEventLoop(installInterrupt=True)

    if delegate.error:
        raise RuntimeError(delegate.error)

    return delegate.location


if __name__ == "__main__":
    location = get_current_location()
    print(location)