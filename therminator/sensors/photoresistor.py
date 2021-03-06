#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import math
import signal
import time
from RPi import GPIO

logger = logging.getLogger(__name__)

def read(pins, capacitance, resistance, voltage=3.3, n=20, timeout=300):
    """Return the average resistance of the photoresistor.

    Keyword arguments:
    pins -- the GPIO pins used for charging and discharging
    capacitance -- the capacitance (in μF) of the capacitor
    resistance -- the resistance (in Ω) of the resistor
    voltage -- the input voltage (in V) (default: 3.3)
    n -- the number of readings over which to average (default: 20)
    timeout -- the number of seconds after which to give up (default: 300)
    """
    logger.debug('Started reading sensor')
    try:
        t1 = time.time()
        reading = _multiread(
            pins,
            C=capacitance,
            R=resistance,
            V=voltage,
            n=n,
            timeout=timeout
        )
        t2 = time.time()
        logger.info('resistance={:.1f}ohms'.format(reading))
        if reading < 0:
            logger.warning('negative resistance will be normalized to 0.0')
            reading = 0
        logger.debug('Finished reading sensor ({:.1f}s)'.format(t2-t1))
        return reading
    except TimeoutError as e:
        logger.warn(e.args)
        raise

def _multiread(pins, C, R, V, n, timeout):
    try:
        signal.signal(signal.SIGALRM, _timeout)
        signal.alarm(timeout)
        data = [_read(pins, C, R, V) for _ in range(n+2)]
        data.sort()
        logger.debug('Discard min and max values: min={:f}us, max={:f}us'.format(data[0], data[-1]))
        mean = sum(data[1:-1]) / n
    finally:
        signal.alarm(0)
    T = mean * (math.e-1)/math.e * V
    return T/C - R

def _timeout(signum, frame):
    raise TimeoutError(
        'Timed out while taking readings from photoresistor. '
        'Try using a smaller capacitor or taking fewer readings.'
    )

def _read(pins, C, R, V):
    a, b = pins
    try:
        _discharge(a, b)
        elapsed_time = _charge(a, b)
        logger.debug('elapsed-time={:f}us'.format(elapsed_time))
        return elapsed_time
    finally:
        _discharge(a, b)

def _discharge(a, b):
    GPIO.setup(a, GPIO.IN)
    GPIO.setup(b, GPIO.OUT)
    GPIO.output(b, GPIO.LOW)
    time.sleep(0.01)

def _charge(a, b):
    GPIO.setup(a, GPIO.OUT)
    GPIO.setup(b, GPIO.IN)
    GPIO.output(a, GPIO.HIGH)
    t1 = time.time()
    while not GPIO.input(b):
        pass
    t2 = time.time()
    return (t2-t1) * 10**6

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pins',
                        metavar=('A', 'B'),
                        type=int,
                        nargs=2,
                        required=True,
                        help='GPIO pins (charging, discharging)')
    parser.add_argument('-c', '--capacitance',
                        metavar='C',
                        type=float,
                        required=True,
                        help='Capacitance (in μF) of capacitor')
    parser.add_argument('-r', '--resistance',
                        metavar='R',
                        type=int,
                        required=True,
                        help='Resistance (in Ω) of resistor')
    parser.add_argument('-v', '--voltage',
                        metavar='V',
                        type=float,
                        default=3.3,
                        help='Voltage (in V) of input voltaage')
    parser.add_argument('-t', '--timeout',
                        type=int,
                        metavar='N',
                        default=300,
                        help='Timeout after N seconds without a reading')
    parser.add_argument('-n',
                        type=int,
                        default=20,
                        help='Number of readings over which to average')
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='Enable deubgging output')
    args = parser.parse_args()

    try:
        if args.debug:
            logging.basicConfig(level=logging.DEBUG)

        GPIO.setmode(GPIO.BCM)
        resistance = read(
            pins=args.pins,
            capacitance=args.capacitance,
            resistance=args.resistance,
            voltage=args.voltage,
            timeout=args.timeout,
            n=args.n
        )
        print(
            'resistance={:.1f}Ω luminosity={:.1f}' \
            .format(resistance, 10**6/resistance)
        )
    finally:
        GPIO.cleanup()
