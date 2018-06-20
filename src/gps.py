from serial import Serial
from micropyGPS.micropyGPS import MicropyGPS
from threading import Thread
from time import sleep

values = {'lat': 0, 'lng': 0, 'altitude': 0}


def run_gps(gps):
    s = Serial('/dev/serial0', 9600, timeout=10)
    s.readline()  # drop first line

    while True:
        sentence = s.readline().decode('utf-8')

        if sentence[0] != '$':
            continue
        for x in sentence:
            gps.update(x)


def update_values(gps):
    global values

    if gps.clean_sentences <= 20:
        return

    values = {
        'lat': gps.latitude[0],
        'lng': gps.longitude[0],
        'altitude': gps.altitude
    }


def start_update_values_loop(gps):
    while True:
        update_values(gps)
        sleep(1.0)


def run_gps_thread(gps):
    gpsthread = Thread(target=run_gps, args=(gps, ))
    gpsthread.daemon = True
    gpsthread.start()


def run_start_update_values_loop_thread(gps):
    gpsthread = Thread(target=start_update_values_loop, args=(gps, ))
    gpsthread.daemon = True
    gpsthread.start()


def init():
    gps = MicropyGPS(9, 'dd')

    run_gps_thread(gps)
    run_start_update_values_loop_thread(gps)


def get():
    return values


if __name__ == '__main__':
    init()

    while True:
        print(values)
        sleep(2.0)
