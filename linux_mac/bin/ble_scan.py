#!/usr/bin/env python3
# -*- coding: utf-8 -*

""" Scans all incoming blue tooth low engery advertisesments, finds
ruuvi tags and reports their mac address and orientation. You can differentiate
tags by turning some upside down or sideways."""

import logging
from time import sleep
from bleson import get_provider, Observer, logger


# Set bleson logging level to error, default is warning
logger.set_level(logging.ERROR)

print("Scanning . . .\n")

tags = {}

def orientation(z):
    """ Returns orientation based off ruuvi tag z axis numbers. """
    if 0.9 < z :
        return "upright"
    if z < -0.9 :
        return "flipped"
    if -0.2 < z < 0.2 :
        return "sideways"

def on_advertisement(advertisement):
    """ Add mac address and orientation of ruuvi tags to the tags dict. """
    mac = advertisement.address.address if advertisement.address is not None else None
    data = advertisement.mfg_data
    if data:
        r = data[0:2].hex()
        if r == "9904":
            Zraw = int.from_bytes(data[13:15], byteorder='big', signed=True)
            accZ = Zraw / 1024
            tags[mac] = orientation(accZ)

adapter = get_provider().get_adapter()

observer = Observer(adapter)
observer.on_advertising_data = on_advertisement

observer.start()
sleep(10)
observer.stop()

print("Mac Address       | Orientation\n-------------------------------")

for m in tags:
    print("{} | {}".format(m, tags[m]))