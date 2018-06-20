from src import gps, bme280
from time import sleep
from datetime import datetime
import csv
from os.path import exists


def write_data(file, write_list):
    writer = csv.writer(file, lineterminator='\n')
    writer.writerow(write_list)


if __name__ == '__main__':
    gps.init()
    bme280.init()

    while True:
        gps_data = gps.get()
        bme_data = bme280.get()
        now = datetime.now()
        date = now.strftime('%Y-%m-%d')
        time = now.strftime('%H:%M:%S')
        file_path = f'csv/{date}.csv'

        if not exists(file_path):
            with open(file_path, 'w') as f:
                f.write(
                    'datetime,lat,lng,altitude,temperature,pressure,humidity\n'
                )

        with open(file_path, 'a') as f:
            write_data(f, [
                f'{date} {time}',
                gps_data['lat'],
                gps_data['lng'],
                gps_data['altitude'],
                bme_data['temperature'],
                bme_data['pressure'],
                bme_data['humidity'],
            ])

        sleep(1 - now.microsecond / 1000000)
