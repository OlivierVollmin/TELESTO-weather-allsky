# Python code continuously running in the backgound, gathering periodic measures
# about temperature, relative pressure, relative humidity as well as continuous measures
# about wind speed, direction, rain etc. All data is averaged and logged to a MariaDB database
#
# Olivier Vollmin
# April 2021

from gpiozero import MCP3008
from gpiozero import Button
from gpiozero import OutputDevice
from RainPHP  import IsCurrentlyRaining #custom function/script
import bme280
import smbus2
import time
import math
import mysql.connector as mariadb
import numpy as np
import os
from datetime import datetime

MARIADB_PERIOD = 300  # sec

# PIN
RAIN_BUCKET_GPIO = 14       # GPIO 14 for bucket interrupt
ANEMOMETER_GPIO = 5         # GPIO 5 for anemometer interrupt
RAIN_HEATER_GPIO = 16       # GPIO 16 to toggle on/off rain sensor heater

# Wind parameters
ANEMOMETER_ADJUSTMENT = 1.18
WIND_DIR_INTERVAL = 5   # sec
WIND_SPEED_INTERVAL = 5  # sec
wind_coeff = ANEMOMETER_ADJUSTMENT * 5
wind_count = 0

# Rain bucket parameters
BUCKET_SIZE = 0.2794  # 1 bucket = 0.2794 mm rain

# Setup ADC conversion
adc = MCP3008(channel=0)
VIN = 3.3  # Using 3.3V as ref for ADC
volts = {0.4: 0.0,
         1.4: 22.5,
         1.2: 45.0,
         2.8: 67.5,
         2.7: 90.0,
         2.9: 112.2,
         2.2: 135.0,
         2.5: 157.5,
         1.8: 180.0,
         2.0: 202.5,
         0.7: 225.0,
         0.8: 247.5,
         0.1: 270.0,
         0.3: 292.5,
         0.2: 315.0,
         0.6: 337.5}

# Setup I2C settings
port = 1
address = 0x76
bus = smbus2.SMBus(port)

# Load BME280 sensor calibrations
bme280.load_calibration_params(bus, address)


##########################################################################
# classes below

class Measures_Class:
    def __init__(self, temperature=20.00, pressure=1013.25, humidity=40.00, 
    wind_dir=0, wind_speed=0, wind_max=0, rain_mm=0, T_dp=0, CurrentlyRaining=False):
        self.temperature = temperature
        self.pressure = pressure
        self.humidity = humidity
        self.wind_dir = wind_dir
        self.wind_speed = wind_speed
        self.wind_max = wind_max
        self.rain_mm = rain_mm
        self.T_dp = T_dp
        self.CurrentlyRaining = CurrentlyRaining


Measures = Measures_Class()
##########################################################################
# functions below


def bucket_tipped():    # Counter for rainfall
    global Measures
    Measures.rain_mm += BUCKET_SIZE


def reset_rainfall():   # Reset counter
    global Measures
    Measures.rain_mm = 0


def get_avg(angles):    # get average accounting for 360° => 0° skip
    sin_sum = 0.0
    cos_sum = 0.0

    for angle in angles:
        r = math.radians(angle)
        sin_sum += math.sin(r)
        cos_sum += math.cos(r)

    flen = float(len(angles))
    s = sin_sum / flen
    c = cos_sum / flen
    arc = math.degrees(math.atan(s / c))
    average = 0.0

    if s > 0 and c > 0:
        average = arc
    elif c < 0:
        average = arc + 180
    elif s < 0 and c > 0:
        average = arc + 360

    return 0.0 if average == 360 else average


def get_value(length=5.0):  # get average sampling over a user defined period of time
    data = []
    start_time = time.time()

    while time.time() - start_time <= length:
        wind = round(adc.value*VIN, 1)
        if wind in volts:
            data.append(volts[wind])

    return get_avg(data)


def spin():  # Counter for anemometer
    global wind_count
    wind_count += 1


def CalculateDewPointTemp():  # Heinrich Gustav Magnus-Tetens formula
    global Measures
    temp = Measures.temperature
    hum = Measures.humidity

    a = 17.27
    b = 237.7

    alpha = a * float(temp) / (b + float(temp)) + np.log(float(hum)/100)
    Measures.T_dp = b * alpha / (a - alpha)


def ReadBME280():
    try:
        # poll and read BME280 sensor values
        bme280_data = bme280.sample(bus, address)
    except OSError as error :
        print(error)
        time.sleep(1)
        # wait some time for the bus
        bme280_data = bme280.sample(bus, 0x76) #force address

    global Measures
    Measures.temperature = bme280_data.temperature
    Measures.pressure = bme280_data.pressure
    Measures.humidity = bme280_data.humidity


def rain_status():  # Check for the presence of water on the sensor
    global Measures
    Measures.CurrentlyRaining = IsCurrentlyRaining()


""" Compute if heating of the rain sensor is required. Heating is required
if the temperature is near or below the dew temperature, or below 0°C.
Heating is also required when it rains to dry the sensor faster."""

def auto_heater_switch():
    global Measures

    if Measures.CurrentlyRaining or (Measures.temperature < (2 + Measures.T_dp)) or (Measures.temperature < 1):
        Heater_Rain.on()

    else:   # No need for hysteresis, to slow for jitter
        Heater_Rain.off()


def write2MariaDB():

    # Setup connection and upload data to MariaDB
    try:
        mariadb_connection = mariadb.connect(
            user='pi', password='TELESTO', database='weatherDB')
        cursor = mariadb_connection.cursor()
        cursor.execute("insert into WEATHER_MEASUREMENT(AMBIENT_TEMPERATURE, AIR_PRESSURE, HUMIDITY, WIND_DIRECTION, WIND_SPEED, WIND_GUST_SPEED, RAINFALL, DEW_POINT_TEMPERATURE, IS_RAINING) values (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
                       (float(Measures.temperature),
                        float(Measures.pressure),
                        float(Measures.humidity),
                        float(Measures.wind_dir),
                        float(Measures.wind_speed),
                        float(Measures.wind_max),
                        float(Measures.rain_mm),
                        float(Measures.T_dp),
                        Measures.CurrentlyRaining))
        mariadb_connection.commit()

    # handle exceptions
    except mariadb.Error as e:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        print(dt_string," Error writing to mariaDB:", e)

    # close connection
    finally:
        mariadb_connection.close()
        cursor.close()

##########################################################################
# GPIO triggered events

rain_bucket = Button(RAIN_BUCKET_GPIO)
rain_bucket.when_pressed = bucket_tipped

wind_button = Button(ANEMOMETER_GPIO)
wind_button.when_pressed = spin


##########################################################################
# Set GPIO pins for relays

# Use OutputDevice() from gpiozero insteat of GPIO
Heater_Rain = OutputDevice(RAIN_HEATER_GPIO) 


##########################################################################
# main loop

while True:
    # reset values for new measurement interval
    wind_dir_list = []
    wind_speed_list = []
    reset_rainfall()

    start_time = time.time()
    while time.time() - start_time <= MARIADB_PERIOD:

        wind_dir = get_value(WIND_DIR_INTERVAL)
        wind_dir_list.append(wind_dir)

        wind_count = 0  # reset interrupt counter
        time.sleep(WIND_SPEED_INTERVAL) # counting interrupt nb during sleep
        wind_speed = wind_coeff * wind_count / WIND_SPEED_INTERVAL / 2
        wind_speed_list.append(wind_speed)

#        rain_status()   #TODO remove
#        print(Measures.CurrentlyRaining)    #TODO remove


    # do stats and save measures in Object
    Measures.wind_dir = get_avg(wind_dir_list)
    Measures.wind_speed = np.mean(wind_speed_list)
    Measures.wind_max = np.max(wind_speed_list)

    # Read BME280 and save in object
    ReadBME280()

    # Compute dew point temperature
    CalculateDewPointTemp()

    # Raining ?
    rain_status()

    # Check if heating is required
    auto_heater_switch()

    # Save data to database
    write2MariaDB()
