#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from bleson import get_provider, Observer, logger
#import sqlite3
import datetime
import pytz
import threading

"""
Script to gather data from ruuvi tag sensors and save it to an sqlite database.
"""

# Dictionary of mac addresses for ruuvi tags and their assigned names
tags = {"F4:65:A0:A6:D9:71": "one",
        "C7:54:71:85:24:77" : "two",
        "D6:80:39:04:06:45" : "three"}

timenow = datetime.datetime.now().astimezone(pytz.utc)

def dt_to_timestamp(dt):
    """ Convert datetime object to timestamp string """
    return dt.strftime("%Y-%m-%d %H:%M:%S %Z %z")

def timestamp_to_dt(ts):
    """ Convert utc timestamp string to datetime object with tz 'UTC' """
    return datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S %Z %z").astimezone(pytz.utc)

def convert_timezone(dt, tz):
    """ Convert datetime object to another timezone, ie 'Europe/Helsinki' """
    return dt.astimezone(pytz.timezone(tz))

timestamp = dt_to_timestamp(timenow)
localtime = dt_to_timestamp(convert_timezone(timenow, 'Europe/Helsinki'))

# DATABASE:

# try:
#     connection = sqlite3.connect('ruuvi.db')
#
#     cursor = connection.cursor()
#
#     cursor.execute('''CREATE TABLE IF NOT EXISTS Sensors (
#             MAC_Address        TEXT     PRIMARY KEY    NOT NULL,
#             Name               TEXT                    NOT NULL,
#             Current_Location   TEXT                    NOT NULL);''')
#
#     cursor.execute('''CREATE TABLE IF NOT EXISTS Readings (
#             MAC_Address    TEXT         NOT NULL references sensors (MAC_Address),
#             Temperature    REAL         NOT NULL,
#             Humidity       REAL         NOT NULL,
#             Pressure       REAL         NOT NULL,
#             Battery        REAL         NOT NULL,
#             Location       TEXT         NOT NULL,
#             Read_Time      TIMESTAMP,
#             PRIMARY KEY (Read_Time, MAC_Address));''')
# except Error as e:
#     print(e)
#
# conn.commit()
# conn.close()

# Set bleson logging level to error, default is warning
logger.set_level(logging.ERROR)

def to_int(bytes):
    """ Converts byte array to signed integer """
    return int.from_bytes(bytes, byteorder='big', signed=True)

def to_uint(bytes):
    """ Converts byte array to unsigned integer """
    return int.from_bytes(bytes, byteorder='big', signed=False)

def parse_data(data):
    """ Parse data into human readable units of measure, save to dict
    https://github.com/ruuvi/ruuvi-sensor-protocols/blob/master/dataformat_05.md """
    payload = data[2:26]
    #atm_pressure = 101325 # Pascal
    temp  =  to_int (payload[ 1: 3]) * 0.005  # units °C
    humid =  to_uint(payload[ 3: 5]) * 0.0025 # percentage
    press = (to_uint(payload[ 5: 7]) + 50000) / 100 # mbar
    #accX  =  to_int (payload[ 7: 9]) / 1024
    #accY  =  to_int (payload[ 9:11]) / 1024
    #accZ  =  to_int (payload[11:13]) / 1024
    voltage = ((to_uint(payload[13:15]) >> 5) + 1600) / 1000 # battery voltage, bitshift right 5 bits
    #signal = (to_uint(payload[13:15]) & 0b00011111) * 2 - 40 ## signal strength (-40dBm to +20dBm range)
    macparse = payload[18:24].hex().upper()
    macaddr = ':'.join(macparse[i:i+2] for i in range(0, 12, 2))
    data_dict = {"tempurature" : round(temp, 1), "humidity" : round(humid, 1), "pressure" : round(press, 4), "battery" : voltage}
    return data_dict

ruuvi_weather = {}

adapter = get_provider().get_adapter()
observer = Observer(adapter)

lock = threading.Lock()
lock.acquire()

def on_advertisement(advertisement):
    # Parse out data from ruuvi tags and save in dict
    mac = advertisement.address.address if advertisement.address is not None else None
    if mac in tags:
        name = tags[mac]
        data = advertisement.mfg_data
        if data:
            ruuvi_weather[name] = parse_data(data)
            if len(ruuvi_weather.keys()) == 3:
                observer.stop()
                lock.release()

observer.on_advertising_data = on_advertisement

observer.start()

lock.acquire() # main thread is blocked here until on_advertisement releases the lock

print(timestamp)
print(localtime)
for tag_name, tag_data in ruuvi_weather.items():
    print("{}: temp: {}°C humidity: {}% pressure: {}mbar, battery: {}v"
            .format(tag_name, tag_data["tempurature"], tag_data["humidity"], tag_data["pressure"], tag_data["battery"]))