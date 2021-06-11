# Python script to read, store CPU temperature in MariaDB and plot last
#
# Olivier Vollmin
# May 2021

from gpiozero import CPUTemperature
from time import sleep, strftime, time
import mysql.connector as mariadb
import matplotlib.pyplot as plt
import matplotlib as mpl
import datetime
import matplotlib.dates as mdates

# get CPU temperature in Celsius
cpu = CPUTemperature()
cpu_temp = cpu.temperature

# get Camera temperature in Celsius
tempfile = open("/home/pi/allsky/temperature.txt","r")
cam_temp = tempfile.read().rstrip()
tempfile.close()

# make a new mariaDB entry and retrieve old values
try:
   mariadb_connection = mariadb.connect(user='pi',password='TELESTO',database='cpu_tempDB')
   cursor1 = mariadb_connection.cursor()
   sql1 = "insert into CPU_TEMP_TABLE (CPU_TEMP, CAMERA_TEMP) values (%s, %s)"
   args = (cpu_temp, float(cam_temp))
   cursor1.execute(sql1,args)
   mariadb_connection.commit()

   cursor2 = mariadb_connection.cursor()
   sql2 = "select * from CPU_TEMP_TABLE where CREATED > DATE_SUB(NOW(), INTERVAL 5 DAY)"
   cursor2.execute(sql2)
   records = cursor2.fetchall()
except mariadb.Error as e:
   print("Error mariaDB:",e)
finally:
   mariadb_connection.close()
   cursor1.close()
   cursor2.close()

# store data in lists
time_list = []
cpu_temp_list = []
cam_temp_list = []

for row in records:
  cpu_temp_list.append(row[1])
  time_list.append(row[2])
  cam_temp_list.append(row[3])

# declare date formatter for plot
myFmt = mdates.DateFormatter('%H:%M')

# generate plot
mpl.use('Agg')

plt.plot(time_list, cpu_temp_list, 'b-')
plt.plot(time_list, cam_temp_list, 'r-')
plt.xlabel('Time')
plt.ylabel('CPU & Camera Sensor Temperature [°C]')
plt.title('Temperature evolution over the last 5 days')
plt.legend(["CPU","Camera"])
plt.grid(axis = 'y')
plt.gca().xaxis.set_major_formatter(myFmt)

# save plot
plt.savefig('/home/pi/weather/cpu_temp.png', dpi = 175)
plt.close()
