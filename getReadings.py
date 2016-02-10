#!/usr/bin/python

# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from __future__ import print_function
import Adafruit_DHT
import time
import sys
import spidev
import time
import os
import math
import mysql.connector

# Function to read SPI data from MCP3008 chip. Channel must be an integer 0-7
def ReadChannel(channel):
	adc = spi.xfer2([1,(8+channel)<<4,0])
	data = ((adc[1]&3) << 8) + adc[2]
  	return data

# Function to convert data to voltage level, rounded to specified number
# of decimal places.
def ConvertVolts(data,places):
	volts = (data * 3.3) / float(1023)
	volts = round(volts,places)
	return volts

# Calculate resistance based on Kirchoff's law
def Resistance(vin, vout, r1):
	return r1/((vin/float(vout)) - 1)

# Calculate illuminance using resistance and chart provided
# http://dlnmh9ip6v2uc.cloudfront.net/datasheets/Sensors/LightImaging/SEN-09088.pdf
def CalculateLux(r):
	return math.e ** ((math.log(r) - 4.21360374)/-0.72150214)

# Sensor should be set to Adafruit_DHT.DHT11, Adafruit_DHT.DHT22,
# or Adafruit_DHT.AM2302.
sensor = Adafruit_DHT.DHT11

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)

# Example using a Beaglebone Black with DHT sensor connected to pin P8_11.
# Example using a Raspberry Pi with DHT sensor connected to GPIO23.
pin = 4

# Define sensor channels
light_channel = 0

# Insert statement for each reading
add_reading = ("INSERT INTO readings "
		"(temperature, humidity, illuminance) "
		"VALUES (%s, %s, %s)")

# Note that sometimes you won't get a reading and
# the results will be null (because Linux can't
# guarantee the timing of calls to read the sensor).
# If this happens try again!

# Database connection
cnx = mysql.connector.connect(user='root', password="TONYHAWK", host='127.0.0.1', database='wstation')
# Database cursor
cursor = cnx.cursor()

# Try to grab a sensor reading.  Use the read_retry method which will retry up
# to 15 times to get a sensor reading (waiting 2 seconds between each retry).
humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
# Grab illuminance reading
light_level = ReadChannel(light_channel)
light_volts = ConvertVolts(light_level,3)
res = Resistance(3.3, light_volts, 10)
lux = CalculateLux(res)

if humidity is not None and temperature is not None:
	reading = (temperature, humidity, lux)
	cursor.execute(add_reading, reading)
	cnx.commit()
	cursor.close()
	cnx.close()
else:
	print("Couldn't get reading!",)
