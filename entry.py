from src import gps, bme280
from time import sleep
from datetime import datetime

if __name__ == '__main__':
    gps.init()
    bme280.init()

    while True:
        now = datetime.now()
        print(str(now), gps.get(), bme280.get())
        sleep(1 - now.microsecond / 1000000)
