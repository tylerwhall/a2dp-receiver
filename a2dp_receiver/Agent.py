#!/usr/bin/python
from __future__ import absolute_import, unicode_literals
try:
    #raise ImportError()
    from gi.repository import GObject
except ImportError:
    import gobject as GObject
import sys
import dbus
import dbus.service
import dbus.mainloop.glib
from dbus.exceptions import DBusException
import logging
BUS_NAME = 'org.bluez'
AGENT_INTERFACE = 'org.bluez.Agent1'

class Agent(dbus.service.Object):
    def __init__(self, bus, path):
        self.bus = bus
        super(Agent, self).__init__(bus, path)

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

    def get_bluez_prop(self, path, interface, prop):
        props = dbus.Interface(self.bus.get_object("org.bluez", path),
                        "org.freedesktop.DBus.Properties")
        return props.Get(interface, prop)

    def set_pairing_mode(self, timeout):
        timeout = dbus.UInt32(timeout)
        self.set_bluez_prop(self.objpath, "PairableTimeout", timeout)
        self.set_bluez_prop(self.objpath, "DiscoverableTimeout", timeout)
        self.set_bluez_prop(self.objpath, "Pairable", True)
        self.set_bluez_prop(self.objpath, "Discoverable", True)

    def get_all_devices(self):
        bluez = dbus.Interface(self.bus.get_object("org.bluez", "/"),
                               "org.freedesktop.DBus.ObjectManager")
        objects = bluez.GetManagedObjects()
        devices = [object for object, interfaces in objects.items() if "org.bluez.Device1" in interfaces]
        return devices

    def get_device_name(self, objpath):
        return self.get_bluez_prop(objpath, "org.bluez.Device1", "Name")

    def remove_all_devices(self):
        devices = self.get_all_devices()
        adapter = dbus.Interface(self.bus.get_object("org.bluez", self.objpath),
                                 "org.bluez.Adapter1")
        for device in devices:
            logging.debug("Removing device %s", device)
            try:
                adapter.RemoveDevice(device)
            except DBusException:
                logging.debug("Removal failed")

    def connect_device(self, path):
        dev = dbus.Interface(self.bus.get_object("org.bluez", path),
                                "org.bluez.Device1")
        dev.Connect()

    def connect_any_device(self):
        devices = self.get_all_devices()
        for device in devices:
            props = dbus.Interface(self.bus.get_object("org.bluez", device),
                            "org.freedesktop.DBus.Properties")
            try:
                if props.Get("org.bluez.Device1", "Connected"):
                    logging.debug("Already connected to %s", device)
                    return
            except DBusException:
                continue

        for device in devices:
            try:
                name = self.get_device_name(device)
                logging.info("Connecting to {}".format(name))
                self.connect_device(device)
                return
            except DBusException:
                logging.debug("Connection failed")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    manager = PairingManager()
    mainloop = GObject.MainLoop()
    manager.connect_any_device()
    #manager.remove_all_devices()
    #manager.set_pairing_mode(60)
    mainloop.run()
