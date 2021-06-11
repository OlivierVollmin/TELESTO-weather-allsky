# this script is used to access the database and retrieve values in order to plot temp/pressure/etc
#
# Olivier Völlmin
# April 2021

from typing import Any
import mysql.connector as mariadb
import matplotlib as mpl
import matplotlib.cbook as cbook
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import datetime
import numpy as np
from windrose import WindroseAxes
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)

# store value in list for futur plots
temperature = []
humidity = []
pressure = []
time = []
wind_dir = []
wind_speed = []
wind_max = []
rain_mm = []
T_dp = []

# Setup connection to MariaDB
try:
    mariadb_connection = mariadb.connect(
        user='pi', password='TELESTO', database='weatherDB')

    sql_select_Query = "select * from WEATHER_MEASUREMENT where WEATHER_MEASUREMENT.CREATED > DATE_SUB(NOW(), INTERVAL 12 HOUR)"

    cursor = mariadb_connection.cursor()
    cursor.execute(sql_select_Query)
    records = cursor.fetchall()  # get all records

# handle exceptions
except mysql.connector.Error as e:
    print("Error reading data from MySQL table", e)

# close connection
finally:
    if mariadb_connection.is_connected():
        mariadb_connection.close()
        cursor.close()


# Extract data and store them in lists
for row in records:
    temperature.append(row[1])
    pressure.append(row[2])
    humidity.append(row[3])
    wind_dir.append(row[4])
    time.append(row[5])
    wind_speed.append(row[6])
    wind_max.append(row[7])
    rain_mm.append(row[8])
    T_dp.append(row[9])

# Compute cumulative rain over period
cum_rain_mm = np.cumsum(rain_mm)

# Declare date formatter for all plots
myFmt = mdates.DateFormatter('%H:%M')

# Generate a plot for temperatur, humidity, etc
mpl.use('Agg')

fig, (ax1, ax2, ax3) = plt.subplots(3)

ax1.plot(time, temperature)
ax1.plot(time, T_dp)
ax1.set_ylabel('[°C]')
ax1.set_title('Temperature & Dew point')
ax1.set_ylim(min(min(temperature), min(T_dp)) - 5, max(temperature) + 5)
ax1.yaxis.set_minor_locator(MultipleLocator(5))

ax2.plot(time, pressure)
ax2.set_ylabel('[hPa]')
ax2.set_title('Pressure')
ax2.yaxis.set_minor_locator(MultipleLocator(5))

ax3.plot(time, humidity)
ax3.set_ylabel('[%]')
ax3.set_title('Relative humidity')
ax3.set_ylim(min(humidity)-5, max(humidity)+5)
ax3.yaxis.set_minor_locator(MultipleLocator(2.5))

plt.gca().xaxis.set_major_formatter(myFmt)

#ax1.grid(which='both')
#ax2.grid(which='both')
#ax3.grid(which='both')

ax1.annotate('%0.2f' % temperature[-1], xy=(1, temperature[-1]), xytext=(8, 0),
             xycoords=('axes fraction', 'data'), textcoords='offset points')
ax1.annotate('%0.2f' % T_dp[-1], xy=(1, T_dp[-1]), xytext=(8, 0),
             xycoords=('axes fraction', 'data'), textcoords='offset points')
ax2.annotate('%0.2f' % pressure[-1], xy=(1, pressure[-1]), xytext=(8, 0),
             xycoords=('axes fraction', 'data'), textcoords='offset points')
ax3.annotate('%0.2f' % humidity[-1], xy=(1, humidity[-1]), xytext=(8, 0),
             xycoords=('axes fraction', 'data'), textcoords='offset points')

fig.autofmt_xdate()
fig.subplots_adjust(hspace=0.5)
fig.savefig('/home/pi/weather/weather_plot.png', dpi=175)
plt.close()

# Generate rainfall histogram
fig2, (ax1, ax3) = plt.subplots(2)

color = 'tab:blue'
ax1.step(time, rain_mm, color=color)
ax1.set_ylabel('[mm/5min]')
ax1.set_title('Rainfall')
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_ylim(0, max(rain_mm)+5)

ax2 = ax1.twinx()

color = 'tab:red'
ax2.step(time, cum_rain_mm, color=color)
ax2.set_ylabel('cumulative [mm]')
ax2.tick_params(axis='y', labelcolor=color)
ax2.set_ylim(0, max(cum_rain_mm)+5)

ax3.plot(time, wind_max)
ax3.set_ylabel('[km/h]')
ax3.set_title('Maximal wind speed')
ax3.set_ylim(0, max(wind_max)+5)

ax1.xaxis.set_major_formatter(myFmt)
ax3.xaxis.set_major_formatter(myFmt)

ax1.grid(which='both')
ax3.grid(which='both')

fig2.autofmt_xdate()
fig2.subplots_adjust(hspace=0.25)
fig2.savefig('/home/pi/weather/rainfall.png', dpi=175)
plt.close()

# Generate windrose

ax5 = WindroseAxes.from_ax()
ax5.bar(wind_dir, wind_speed, normed=True, opening=0.8,
        edgecolor='white', bins=np.arange(0, 8, 1))
ax5.set_legend(title="wind speed km/h", loc='lower right',
               bbox_to_anchor=(1.1, 0.8))
ax5.set_xticklabels(['E','NE', 'N', 'NW',  'W', 'SW', 'S', 'SE'])

plt.savefig('/home/pi/weather/windrose.png', dpi=175)
plt.close()
