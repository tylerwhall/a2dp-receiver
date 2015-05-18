#!/usr/bin/python
from __future__ import absolute_import, unicode_literals
from gi.repository import GObject
import sys
import dbus
import dbus.service
import dbus.mainloop.glib
import logging
BUS_NAME = 'org.bluez'
AGENT_INTERFACE = 'org.bluez.Agent1'

class Agent(dbus.service.Object):
    def __init__(self, bus, path):
        self.bus = bus
        super().__init__(bus, path)

    def set_trusted(self, path):
        props = dbus.Interface(self.bus.get_object("org.bluez", path),
                        "org.freedesktop.DBus.Properties")
        props.Set("org.bluez.Device1", "Trusted", True)
    @dbus.service.method(AGENT_INTERFACE,
                    in_signature="", out_signature="")
    def Release(self):
        logging.debug("Release")
        mainloop.quit()
    @dbus.service.method(AGENT_INTERFACE,
                    in_signature="os", out_signature="")
    def AuthorizeService(self, device, uuid):
        logging.debug("AuthorizeService (%s, %s)" % (device, uuid))
        return
    @dbus.service.method(AGENT_INTERFACE,
                    in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        logging.debug("RequestPinCode (%s)" % (device))
        self.set_trusted(device)
        return "0000"
    @dbus.service.method(AGENT_INTERFACE,
                    in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        logging.debug("RequestPasskey (%s)" % (device))
        self.set_trusted(device)
        return dbus.UInt32(0)
    @dbus.service.method(AGENT_INTERFACE,
                    in_signature="ouq", out_signature="")
    def DisplayPasskey(self, device, passkey, entered):
        logging.debug("DisplayPasskey (%s, %06u entered %u)" %
                        (device, passkey, entered))
    @dbus.service.method(AGENT_INTERFACE,
                    in_signature="os", out_signature="")
    def DisplayPinCode(self, device, pincode):
        logging.debug("DisplayPinCode (%s, %s)" % (device, pincode))
    @dbus.service.method(AGENT_INTERFACE,
                    in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey):
        logging.debug("RequestConfirmation (%s, %06d)" % (device, passkey))
        self.set_trusted(device)
        return
    @dbus.service.method(AGENT_INTERFACE,
                    in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        logging.debug("RequestAuthorization (%s)" % (device))
        return
    @dbus.service.method(AGENT_INTERFACE,
                    in_signature="", out_signature="")
    def Cancel(self):
        logging.debug("Cancel")

class PairingManager:
    def __init__(self):
        self.objpath = "/org/bluez/hci0"
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SystemBus()
        path = "/co/telnet/agent"
        agent = Agent(self.bus, path)
        obj = self.bus.get_object(BUS_NAME, "/org/bluez");
        manager = dbus.Interface(obj, "org.bluez.AgentManager1")
        capability = "KeyboardDisplay"
        manager.RegisterAgent(path, capability)
        logging.debug("Agent registered")
        manager.RequestDefaultAgent(path)

    def set_bluez_prop(self, path, prop, val):
        props = dbus.Interface(self.bus.get_object("org.bluez", path),
                        "org.freedesktop.DBus.Properties")
        props.Set("org.bluez.Adapter1", prop, val)

    def set_pairing_mode(self, timeout):
        self.set_bluez_prop(self.objpath, "PairableTimeout", timeout)
        self.set_bluez_prop(self.objpath, "DiscoverableTimeout", timeout)
        self.set_bluez_prop(self.objpath, "Pairable", True)
        self.set_bluez_prop(self.objpath, "Discoverable", True)

    def dev_connect(path):
        dev = dbus.Interface(self.bus.get_object("org.bluez", path),
                                "org.bluez.Device1")
        dev.Connect()
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    manager = PairingManager()
    mainloop = GObject.MainLoop()
    manager.set_pairing_mode(dbus.UInt32(10))
    mainloop.run()
