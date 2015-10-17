try:
    #raise ImportError()
    from gi.repository import GLib
except ImportError:
    import glib as GLib
import dbus
import logging
import subprocess
import time
from . import CommandListener
from . import Agent
import serial

MEDIA_PLAYER_IFC = 'org.bluez.MediaPlayer1'

class AvrcpPlayers:
    def __init__(self, bus):
        self.bus = bus
        self.players = []
        try:
            omanager = dbus.Interface(bus.get_object('org.bluez', '/'),
                                      dbus_interface = 'org.freedesktop.DBus.ObjectManager')
            paths = omanager.GetManagedObjects()
            players = [path for path, interfaces in paths.items() if MEDIA_PLAYER_IFC in interfaces]
        except DBusException:
            logging.error("Failed to get players %s" % e)
            return

        logging.debug("Found players %s" % players)
        for player in players:
            try:
                p = dbus.Interface(bus.get_object('org.bluez', player),
                                      dbus_interface = MEDIA_PLAYER_IFC)
                self.players.append(p)
            except DBusException:
                logging.error("Failed to create proxy for %s" % player)
                continue

    def call_safe(self, method):
        for player in self.players:
            try:
                getattr(player, method)()
            except DBusException:
                logging.error("Method %s failed for %s", method, player)
                return False
        return len(self.players) > 0

    def play(self):
        return self.call_safe("Play");

    def pause(self):
        return self.call_safe("Pause");

    def next(self):
        return self.call_safe("Next");

    def previous(self):
        return self.call_safe("Previous");

class Controller:
    def __init__(self, f_in):
        self.bus = dbus.SystemBus()
        self.listener = CommandListener.CommandListener(f_in, self)
        self.pairing = Agent.PairingManager()

    def list(self, n):
        logging.debug("LIST %d", n)
        time.sleep(2.5) # Audio mutes temporarily when this command is sent
        if n == 6:
            self.pairing.set_pairing_mode(60)
            logging.info("Pairing mode active for 60 seconds")
        elif n == 5:
            self.pairing.remove_all_devices()
            logging.info("Removed all paired devices")
        else:
            logging.info("Unknown command %d" % n)

    def play(self):
        self.pairing.connect_any_device()
        if not AvrcpPlayers(self.bus).play():
            # The player interface takes some time to appear after connecting.
            # Wait a short period if the command failed
            time.sleep(0.5)
            AvrcpPlayers(self.bus).play()

    def pause(self):
        AvrcpPlayers(self.bus).pause()

    def next(self):
        AvrcpPlayers(self.bus).next()

    def previous(self):
        AvrcpPlayers(self.bus).previous()

class SpeechFilter(logging.Filter):
    def filter(self, record):
        if record.levelno == logging.INFO:
            try:
                subprocess.call(["espeak", "-v", "en-sc", record.msg])
            except:
                pass
        return True

def main():
    import sys

    if len(sys.argv) != 2:
        print("First argument must be serial device or - for stdin")
        sys.exit(1)

    if sys.argv[1] == '-':
        f = sys.stdin
    else:
        f = serial.Serial(sys.argv[1], 19200)

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('').addFilter(SpeechFilter())

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    loop = GLib.MainLoop()

    Controller(f)
    logging.info("Bluetooth ready")

    loop.run()
