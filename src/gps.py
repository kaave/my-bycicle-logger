from serial import Serial
from micropyGPS.micropyGPS import MicropyGPS
from threading import Thread
import time


def run_gps():
    s = Serial('/dev/serial0', 9600, timeout=10)
    s.readline()  # drop first line

    while True:
        sentence = s.readline().decode('utf-8')

        if sentence[0] != '$':
            continue
        for x in sentence:
            gps.update(x)


def run_gps_thread():
    gpsthread = Thread(target=run_gps, args=())
    gpsthread.daemon = True
    gpsthread.start()


if __name__ == '__main__':
    gps = MicropyGPS(9, 'dd')
    run_gps_thread()

    while True:
        if gps.clean_sentences > 20:
            hour = gps.timestamp[0] % 24
            minute = gps.timestamp[1]
            second = gps.timestamp[2]

            print('%2d:%02d:%04.1f' % (hour, minute, second))
            print('緯度経度: %2.8f, %2.8f' % (gps.latitude[0], gps.longitude[0]))
            print('海抜: %f' % gps.altitude)
            print(gps.satellites_used)
            print('衛星番号: (仰角, 方位角, SN比)')
            for k, v in gps.satellite_data.items():
                print('%d: %s' % (k, v))
            print('')

        time.sleep(1.0)
