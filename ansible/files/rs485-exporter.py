#!/usr/bin/python3

import random
import time
import serial
import sys

from prometheus_client import start_http_server, Summary, Gauge
import rs485_module as rs485

ENERGOMERA = None
ENERGOMERA_TOTAL = Gauge('energomera_total_kw_h', "Total amount of kw/h on Energomera")
ENERGOMERA_T1 = Gauge('energomera_t1_kw_h', "T1 amount of kw/h on Energomera")
ENERGOMERA_T2 = Gauge('energomera_t2_kw_h', "T2 amount of kw/h on Energomera")
ENERGOMERA_U = Gauge('energomera_u_volts', "current U volts on Energomera")
ENERGOMERA_A = Gauge('energomera_a_ampers', "current A amount Energomera")
ENERGOMERA_P = Gauge('energomera_power_watt', "current power watts on Energomera")



def calculate_energomera_total():
    TOTAL = ENERGOMERA.cmd('ET0PE(1)')
    ENERGOMERA_TOTAL.set(TOTAL)

    T1, T2 = ENERGOMERA.cmd('ET0PE(2,2)')
    ENERGOMERA_T1.set(T1)
    ENERGOMERA_T2.set(T2)

    U = ENERGOMERA.cmd('VOLTA()')
    ENERGOMERA_U.set(U)

    A = ENERGOMERA.cmd('CURRE()')
    ENERGOMERA_A.set(A)

    P = ENERGOMERA.cmd('POWEP()') * 1000
    ENERGOMERA_P.set(P)

    print("Energomera stats updated")

if __name__ == '__main__':
    # Start up the server to expose the metrics
    start_http_server(8000)
    # Generate some requests.
    while True:
        time.sleep(20)
        try:
            ENERGOMERA = rs485.Counter('/dev/ttyUSB0', False)
            ENERGOMERA.mode('w')
        except Exception as e:
            print(e, file=sys.stderr)
            continue

        calculate_energomera_total()
