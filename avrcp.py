from gi.repository import GLib, Gio
import dbus
import logging
import CommandListener
import Agent
import serial

MEDIA_PLAYER_IFC = 'org.bluez.MediaPlayer1'

class AvrcpPlayers:
    def __init__(self, bus):
        self.bus = bus
        self.players = []
        try:
            paths = bus.call_sync('org.bluez', '/', 'org.freedesktop.DBus.ObjectManager', 'GetManagedObjects',
                    None, GLib.VariantType.new('(a{oa{sa{sv}}})'), 0, -1, None)
            paths = paths.unpack()[0]
            players = [path for path, interfaces in paths.items() if MEDIA_PLAYER_IFC in interfaces]
        except GLib.Error as e:
            logging.error("Failed to get players %s" % e)
            return

        logging.debug("Found players %s" % players)
        flags = Gio.DBusProxyFlags.DO_NOT_LOAD_PROPERTIES
        for player in players:
            try:
                p = Gio.DBusProxy.new_sync(bus, flags, None, 'org.bluez', player, MEDIA_PLAYER_IFC, None)
                self.players.append(p)
            except GLib.Error:
                logging.error("Failed to create proxy for %s" % player)
                continue

    def call_safe(self, method):
        for player in self.players:
            try:
                getattr(player, method)()
            except GLib.Error:
                logging.error("Method %s failed for %s", method, player)

    def play(self):
        self.call_safe("Play");

    def pause(self):
        self.call_safe("Pause");

    def next(self):
        self.call_safe("Next");

    def previous(self):
        self.call_safe("Previous");

class Controller:
    def __init__(self, f_in):
        self.bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
        self.listener = CommandListener.CommandListener(f_in, self)
        self.pairing = Agent.PairingManager()

    def list(self, n):
        logging.debug("LIST %d", n)
        if n == 6:
            self.pairing.set_pairing_mode(60)
            logging.info("Pairing mode active for 60 seconds")
        elif n == 5:
            self.pairing.remove_all_devices()
            logging.info("Removed all paired devices")
        else:
            logging.info("Unknown command %d", n)

    def play(self):
        self.pairing.connect_any_device()
        AvrcpPlayers(self.bus).play()

    def pause(self):
        AvrcpPlayers(self.bus).pause()

    def next(self):
        AvrcpPlayers(self.bus).next()

    def previous(self):
        AvrcpPlayers(self.bus).previous()

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("First argument must be serial device or - for stdin")
        sys.exit(1)

    if sys.argv[1] == '-':
        f = sys.stdin
    else:
        f = serial.Serial(sys.argv[1], 19200)

    logging.basicConfig(level=logging.DEBUG)

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    loop = GLib.MainLoop()

    Controller(f)
    logging.info("Bluetooth ready")

    loop.run()
