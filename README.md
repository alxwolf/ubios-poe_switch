# UniFi switches on UDM (Pro): Turn PoE on or off via REST-API

A small python script to switch PoE power of an UniFi switch, controlled by a UDM (Pro), on or off.

Handy if you want automate the (de-)activation of cameras or WLAN Access Points. Can easily be integrated in projects like openHAB or Home Assistant, including control by Apple HomeKit or Google Alexa.

## Usage

```
usage: poe_switch.py [-h] [-v] controller username password mac ports state

Change the PoE Mode of UniFi switches controlled by a UDM (Pro).

positional arguments:
  controller     hostname or IP address of UniFi Controller
  username       username with admin rights on UniFi Controller
  password       corresponding password for admin user
  mac            MAC address (with or without colons) of switch
  ports          port numbers to acquire new state (list separated by comma,
                 e.g., '5,6,7')
  state          desired state of PoE ports, e.g., 'auto' or 'off'

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  increase output verbosity
```

`python3 poe_switch.py udm.example.org IamAdmin P4ssword fcec12345678 6,7 auto` will turn on the PoE (in mode `auto`) for ports 6 and 7 of the UniFi PoE switch with MAC address fc:ec:12:34:56:78.

## Tested on
Firmware 1.10.0, Network 6.2.26
