# Weather station code directory

In this directory there are 2 main scripts (and corresponding log files), namely :

* **Measure.py** : This script is running non-stop, gathering weather data and storing them in the Database
* **plot.py** : This script is called every 5 minutes by Cron to generate new plots (.png files in the directory)

Besides those 2 main scripts there is also:
* **RainPHP.py** which is periodically called within **Measure.py** and whenever the webpage is refresh. It checks the current status of the capacitif rain sensor and return a True/False value.
* **CPU_temp** which is called every 5 minutes to read, store and plot the Raspberry Pi CPU and All-Sky camera sensor temperature.

The other scripts found in the directory were used for calibration or testing purpose.
