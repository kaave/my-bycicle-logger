from threading import Thread
from time import sleep

cnt = 0


def counter():
    global cnt

    while True:
        cnt += 1
        sleep(1)


def run_thread():
    gpsthread = Thread(target=counter, args=())
    gpsthread.daemon = True
    gpsthread.start()


def get():
    return cnt


def init():
    run_thread()
