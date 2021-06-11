# This Python script runs everytime the user refreshes the webpage
# /!\ PERMISSIONS: user www-data needs to be in gpio group
#
# Olivier Vollmin
# April 2021

from gpiozero import Button

def IsCurrentlyRaining():
    CAPACITIF_RAIN_GPIO = 4     # GPIO 4 for capacitif rain sensor

    # Set pins
    rain_detected = Button(CAPACITIF_RAIN_GPIO)  # attach GPIO
    # Read sensor
    CurrentlyRaining = rain_detected.is_pressed

    if CurrentlyRaining:    # raining
        print("True")
    else:                   # not raining
        print("False")

    return CurrentlyRaining

def main():
    # Chek for rain on the sensor
    IsCurrentlyRaining()

# needed to run when called as a script
if __name__ == "__main__":
    main()