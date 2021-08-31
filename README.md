# UniFi switches on UDM (Pro): Turn PoE on or off via REST-API

A small python script to switch PoE power of an UniFi switch, controlled by a UDM (Pro), on or off.

Handy if you want automate the (de-)activation of cameras or WLAN Access Points. Can easily be integrated in projects like openHAB or Home Assistant, including control by Apple HomeKit or Google Alexa.

## Usage

`python3 poe_switch.py udm.example.org IamAdmin P4ssword fcec12345678 6,7 auto`

will turn on the PoE (in mode `auto`) for ports 6 and 7 of the UniFi PoE switch with MAC address fc:ec:12:34:56:78.

## Tested on
Firmware 1.10.0, Network 6.2.26
