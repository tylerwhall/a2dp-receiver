from gi.repository import GLib, Gio
import fcntl
import os
import re
import logging

class AsyncReader:
    def __init__(self, f, callback):
        self.f = f
        self.callback = callback
        self.buf = ""
        fd = f.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl. F_SETFL, fl | os.O_NONBLOCK)
        channel = GLib.IOChannel.unix_new(f.fileno())
        GLib.io_add_watch(channel, GLib.PRIORITY_DEFAULT, GLib.IO_IN, self.data_in, None)

    def data_in(self, channel, condition, data):
        newdata = self.f.read()
        if type(newdata) == bytes:
            newdata = str(newdata, 'ascii')
        self.buf += newdata
        while True:
            match = re.match("(.*)[\n\r]+((?:.|[\n\r])*)", self.buf)
            if not match:
                break
            line = match.group(1)
            self.buf = match.group(2)
            if len(line):
                logging.debug("Got line: %s" % line)
                self.callback(line)

        return True

COMMAND_MAP = {
    "PLAY":     "play",
    "MENABLE":  "play",
    "MDISABLE": "pause",
    "NEXT":     "next",
    "PREVIOUS": "previous",
}

class CommandListener:
    def __init__(self, f, controller):
        self.controller = controller
        self.reader = AsyncReader(f, self.handle_line)
    
    def handle_line(self, line):
        try:
            # Special case for LISTN command
            if line.startswith("LIST"):
                n = int(line[4])
                self.controller.list(n)
            else:
                func = COMMAND_MAP[line]
                getattr(self.controller, func)()
        except Exception as e:
            logging.debug("Unhandled command %s: %s", line, e)

if __name__ == "__main__":
    import sys
    class Controller:
        def list(self, n):
            print("LIST", n)

        def play(self):
            print("play")

    logging.basicConfig(level=logging.DEBUG)
    CommandListener(sys.stdin, Controller())
    loop = GLib.MainLoop()
    loop.run()
