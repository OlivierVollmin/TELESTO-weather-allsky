from gpiozero import Button
import time
import math

ANEMOMETER_ADJUSTMENT = 1.18

wind_count = 0  
wind_coeff = ANEMOMETER_ADJUSTMENT * 5
wind_interval = 5

# Counter for anemometer
def spin():
    global wind_count
    wind_count += 1

Wind_button = Button(5)
Wind_button.when_pressed = spin

while True:
    wind_count = 0
    time.sleep(wind_interval)
    
    wind_speed = wind_coeff * wind_count /(wind_interval*2)
    print("wind speed = ", wind_speed)
