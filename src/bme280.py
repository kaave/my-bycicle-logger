from smbus2 import SMBus
from threading import Thread
from time import sleep

values = {'temperature': 15.0, 'pressure': 1000, 'humidity': 50.0}


def get_dig_temperature(calib):
    dig_temperature = []
    dig_temperature.append((calib[1] << 8) | calib[0])
    dig_temperature.append((calib[3] << 8) | calib[2])
    dig_temperature.append((calib[5] << 8) | calib[4])

    for i in range(1, 2):
        if dig_temperature[i] & 0x8000:
            dig_temperature[i] = (-dig_temperature[i] ^ 0xFFFF) + 1

    return dig_temperature


def get_dig_pressure(calib):
    dig_pressure = []

    dig_pressure.append((calib[7] << 8) | calib[6])
    dig_pressure.append((calib[9] << 8) | calib[8])
    dig_pressure.append((calib[11] << 8) | calib[10])
    dig_pressure.append((calib[13] << 8) | calib[12])
    dig_pressure.append((calib[15] << 8) | calib[14])
    dig_pressure.append((calib[17] << 8) | calib[16])
    dig_pressure.append((calib[19] << 8) | calib[18])
    dig_pressure.append((calib[21] << 8) | calib[20])
    dig_pressure.append((calib[23] << 8) | calib[22])

    for i in range(1, 8):
        if dig_pressure[i] & 0x8000:
            dig_pressure[i] = (-dig_pressure[i] ^ 0xFFFF) + 1

    return dig_pressure


def get_dig_humidity(calib):
    dig_humidity = []

    dig_humidity.append(calib[24])
    dig_humidity.append((calib[26] << 8) | calib[25])
    dig_humidity.append(calib[27])
    dig_humidity.append((calib[28] << 4) | (0x0F & calib[29]))
    dig_humidity.append((calib[30] << 4) | ((calib[29] >> 4) & 0x0F))
    dig_humidity.append(calib[31])

    for i in range(0, 6):
        if dig_humidity[i] & 0x8000:
            dig_humidity[i] = (-dig_humidity[i] ^ 0xFFFF) + 1

    return dig_humidity


def get_calib_param(i2c_address, bus):
    calib = []

    for i in range(0x88, 0x88 + 24):
        calib.append(bus.read_byte_data(i2c_address, i))

    calib.append(bus.read_byte_data(i2c_address, 0xA1))

    for i in range(0xE1, 0xE1 + 7):
        calib.append(bus.read_byte_data(i2c_address, i))

    return {
        'temperture': get_dig_temperature(calib),
        'pressure': get_dig_pressure(calib),
        'humidity': get_dig_humidity(calib),
    }


def get_pressure(digP, adc_P, t_fine):
    pressure = 0.0

    v1 = (t_fine / 2.0) - 64000.0
    v2 = (((v1 / 4.0) * (v1 / 4.0)) / 2048) * digP[5]
    v2 = v2 + ((v1 * digP[4]) * 2.0)
    v2 = (v2 / 4.0) + (digP[3] * 65536.0)
    v1 = (((digP[2] * (((v1 / 4.0) * (v1 / 4.0)) / 8192)) / 8) + (
        (digP[1] * v1) / 2.0)) / 262144
    v1 = ((32768 + v1) * digP[0]) / 32768

    if v1 == 0:
        return 0

    pressure = ((1048576 - adc_P) - (v2 / 4096)) * 3125

    if pressure < 0x80000000:
        pressure = (pressure * 2.0) / v1
    else:
        pressure = (pressure / v1) * 2

    v1 = (digP[8] * (((pressure / 8.0) * (pressure / 8.0)) / 8192.0)) / 4096
    v2 = ((pressure / 4.0) * digP[7]) / 8192.0
    pressure = pressure + ((v1 + v2 + digP[6]) / 16.0)

    return pressure / 100


def get_temp(digT, adc_T):
    t_fine = 0.0
    v1 = (adc_T / 16384.0 - digT[0] / 1024.0) * digT[1]
    v2 = (adc_T / 131072.0 - digT[0] / 8192.0) * (
        adc_T / 131072.0 - digT[0] / 8192.0) * digT[2]
    t_fine = v1 + v2

    return t_fine / 5120.0, t_fine


def get_humid(digH, adc_H, t_fine):
    var_h = t_fine - 76800.0
    if var_h != 0:
        var_h = (adc_H - (digH[3] * 64.0 + digH[4] / 16384.0 * var_h)) * (
            digH[1] / 65536.0 * (1.0 + digH[5] / 67108864.0 * var_h *
                                 (1.0 + digH[2] / 67108864.0 * var_h)))
    else:
        return 0

    var_h = var_h * (1.0 - digH[0] * var_h / 524288.0)

    if var_h > 100.0:
        var_h = 100.0
    elif var_h < 0.0:
        var_h = 0.0

    return var_h


def setup(i2c_address, bus):
    osrs_t = 1  # Temperature oversampling x 1
    osrs_p = 1  # Pressure oversampling x 1
    osrs_h = 1  # Humidity oversampling x 1
    mode = 3  # Normal mode
    t_sb = 5  # Tstandby 1000ms
    filter = 0  # Filter off
    spi3w_en = 0  # 3-wire SPI Disable

    ctrl_meas_reg = (osrs_t << 5) | (osrs_p << 2) | mode
    config_reg = (t_sb << 5) | (filter << 2) | spi3w_en
    ctrl_hum_reg = osrs_h
    bus.write_byte_data(i2c_address, 0xF2, ctrl_hum_reg)
    bus.write_byte_data(i2c_address, 0xF4, ctrl_meas_reg)
    bus.write_byte_data(i2c_address, 0xF5, config_reg)


def get_data_bme280():
    global values

    i2c_address = 0x76
    bus_number = 1
    bus = SMBus(bus_number)
    setup(i2c_address, bus)

    digs = get_calib_param(i2c_address, bus)
    data = []

    while True:
        for i in range(0xF7, 0xF7 + 8):
            data.append(bus.read_byte_data(i2c_address, i))
        pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        hum_raw = (data[6] << 8) | data[7]

        temp, t_fine = get_temp(digs['temperture'], temp_raw)
        pressure = get_pressure(digs['pressure'], pres_raw, t_fine)
        humid = get_humid(digs['humidity'], hum_raw, t_fine)

        values = {'temperature': temp, 'pressure': pressure, 'humidity': humid}
        sleep(1)


def run_thread():
    get_thread = Thread(target=get_data_bme280, args=())
    get_thread.daemon = True
    get_thread.start()


def init():
    run_thread()


def get():
    return values


if __name__ == '__main__':
    print(get())
