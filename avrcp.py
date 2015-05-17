from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib, Gio
import logging

MEDIA_PLAYER_IFC = 'org.bluez.MediaPlayer1'

class AvrcpPlayers:
    def __init__(self, bus):
        self.bus = bus
        paths = bus.call_sync('org.bluez', '/', 'org.freedesktop.DBus.ObjectManager', 'GetManagedObjects',
                None, GLib.VariantType.new('(a{oa{sa{sv}}})'), 0, -1, None)
        paths = paths.unpack()[0]
        players = [path for path, interfaces in paths.items() if MEDIA_PLAYER_IFC in interfaces]
        logging.info("Found players %s" % players)
        flags = Gio.DBusProxyFlags.DO_NOT_LOAD_PROPERTIES
        self.players = []
        for player in players:
            try:
                p = Gio.DBusProxy.new_sync(bus, flags, None, 'org.bluez', player, MEDIA_PLAYER_IFC, None)
                self.players.append(p)
            except GLib.Error:
                logging.error("Failed to create proxy for %s" % player)
                continue

    def play(self):
        for player in self.players:
            player.Play()

    def pause(self):
        for player in self.players:
            player.Pause()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    loop = GLib.MainLoop()

    bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)

    try:
        players = AvrcpPlayers(bus)
    except GLib.Error:
        print("error")
        raise

    players.play()

    loop.run()
