from gpiozero import MCP3008
import time
import math

R1 = 4700  # Using a 4.7kOhm resistor
VIN = 3.3  # Using 3.3V as ref

adc = MCP3008(channel=0)
count = 0
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


def get_avg(angles):  # get average accounting for 360° => 0° skip
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


def get_value(length=5):  # get average sampling over a user defined period of time
    data = []
#    print("Measuring wind direction for %d seconds..." % length)
    start_time = time.time()

    while time.time() - start_time <= length:
        wind = round(adc.value*VIN, 1)
        if not wind in volts:
            print('unknown value: ' + str(wind))
        else:
            data.append(volts[wind])
    return get_avg(data)


while True:
    time.sleep(0.1)
    wind_dur = 5  # sec
    print('Averaged wind direction ' + str(round(get_value(wind_dur), 2)
                                           ) + ' for ' + str(wind_dur) + 'seconds')
