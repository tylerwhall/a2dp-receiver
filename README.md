# a2dp-receiver

Make Linux act like a standalone bluetooth audio receiver. Commerical bluetooth
audio units have unpredictable audio quality and must be purchased specifically
to connect to a particular audio and control interface, e.g. iPod or XM
connection to a car's head unit. This code is intended to work with a VWCDPIC
adapter for older VW/Audi CD changer inputs, but should be simple enough to
adapt to other interfaces.

## Features

* Bluez5 agent for pairing
* Serial command interface (currently intended for interfacing with a VW head unit)
  * Sends AVRCP control (play, pause, next, previous)
  * Commands for entering pairing mode (PIN 0000 to pair) and deleting all pairings
* Text to speech audio feedback for status information
* [Companion Yocto layer](https://github.com/tylerwhall/meta-a2dp-receiver) for building a headless audio appliance

## Requirements

* Python 2.7 or 3
* Bluez5
* PulseAudio with Bluetooth plugins. These do the heavy lifting and require no configuration.
* Tested with a USB Bluetooth HCI adapter

## Todo

* Separate VWCDPIC command parsing into a plugin to support different control inputs
* Register for D-Bus signals instead of polling for adapter presence, connecting, etc.

## Contributing

Send a merge request on GitHub. Modularizing the command input will probably be
the first order of business for someone wanting to connect to their car or
other control method.
