#!/usr/bin/python
 
import spidev
import time
import os
import numpy as np
import mysql.connector

# Insert statement for each reading
add_reading = ("INSERT INTO readings "
                "(illuminance) "
                "VALUES (%s)")

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)
 
# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def ReadChannel(channel):
	adc = spi.xfer2([1,(8+channel)<<4,0])
	data = ((adc[1]&3) << 8) + adc[2]
  	return data
 
# Function to convert data to voltage level,
# rounded to specified number of decimal places.
def ConvertVolts(data,places):
	volts = (data * 3.3) / float(1023)
	volts = round(volts,places)
	return volts

def Resistance(vin, vout, r1):
	return r1/((vin/float(vout)) - 1)

def CalculateLux(r):
	return np.e ** ((np.log(r) - 4.21360374)/-0.72150214)
 
# Define sensor channels
light_channel = 0
 
# Define delay between readings
delay = 15
 
while True:
	# Database connection
	cnx = mysql.connector.connect(user='root', password='TONYHAWK', host='127.0.0.1', database='wstation')
	# Database cursor
	cursor = cnx.cursor()
 
	# Read the light sensor data
	light_level = ReadChannel(light_channel)
	light_volts = ConvertVolts(light_level,3)
	res = Resistance(3.3, light_volts, 10)
	lux = CalculateLux(res)

	reading = lux
	cursor.execute(add_reading, reading)
	cnx.commit()
	cursor.close()
	cnx.close()
 
	# Print out results
	# print "--------------------------------------------"
	# print("Light: {} ({}V) ({}O) ({}Lux)".format(light_level,light_volts,res,lux))
 
	# Wait before repeating loop
	time.sleep(delay)
