from gpiozero import Button
import time
from datetime import datetime

CAPACITIF_RAIN_GPIO = 4     # GPIO 4 for capacitif rain sensor

rain_detected = Button(CAPACITIF_RAIN_GPIO)

def rain_status():  # Check for the presence of water on the sensor
    global Measures
    CurrentlyRaining = rain_detected.is_pressed

while True:
    CurrentlyRaining = False # reset rain flag

    start_time = time.time()

    while time.time() - start_time <= 20:
        time.sleep(1)
        rain_status()
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print(current_time, "raining ? " + str(CurrentlyRaining))