import dbus
import time

MEDIA_PLAYER_IFC = 'org.bluez.MediaPlayer1'

class AvrcpPlayer:
    def __init__(self, bus_object):
        self.bus_object = bus_object

    def get_prop(self, prop):
        return self.bus_object \
                .get_dbus_method('Get',
                        dbus_interface='org.freedesktop.DBus.Properties')(MEDIA_PLAYER_IFC, prop)

    def call_method(self, name):
        self.bus_object.get_dbus_method(name, dbus_interface=MEDIA_PLAYER_IFC)()

    def next(self):
        self.call_method('Next')

if __name__ == "__main__":
    bus = dbus.SystemBus()

    bluez = bus.get_object('org.bluez', '/')
    paths = dbus.Interface(bluez, 'org.freedesktop.DBus.ObjectManager') \
            .get_dbus_method('GetManagedObjects')()

    players = []
    for path, interfaces in paths.items():
        if MEDIA_PLAYER_IFC in interfaces:
            print(path)
            players.append(AvrcpPlayer(bus.get_object('org.bluez', path)))

    for p in players:
        p.next()
        while True:
            print(p.get_prop('Status'))
            print(p.get_prop('Position'))
            print(p.get_prop('Track')['Duration'])
            print(p.get_prop('Track'))
            time.sleep(1)
