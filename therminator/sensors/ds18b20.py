#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import time

def read(file, timeout=10, wait=0.2, threshold=32):
    """Return the external temperature.

    Keyword arguments:
    file -- the path to the 1-wire serial interface file
    timeout -- number of seconds without a reading after which to give up
    wait -- number of seconds to wait after a failed read before retying
    threshold -- log a warning if temperature exceed threshold

    Although the DS18B20 only measures the temperature, this method returns a
    two-element tuple to allow easier interchangibility with the DHT22 which
    returns temperature and humidity.
    """
    logger = logging.getLogger(__name__)
    logger.debug('Started reading sensor')
    t1 = time.time()
    try:
        temp = _read(file, timeout, wait)
    except (RuntimeError, FileNotFoundError) as e:
        logger.warn(e.args)
        raise
    t2 = time.time()
    if temp > threshold:
        logger.warning(
            'temp {:.1f}C exceeds threshold {:.1f}C' \
            .format(temp, threshold)
        )
    logger.info('temp={:.1f}C'.format(temp))
    logger.debug('Finished reading sensor ({:.1f}s)'.format(t2-t1))
    return temp, None

def _read(file, timeout, wait):
    for _ in range(int(timeout/wait)):
        data = _raw_read(file)
        if data[0].endswith('YES'):
            i = data[1].find('t=')
            return float(data[1][i+2:]) / 1000
        time.sleep(wait)
    raise RuntimeError('Timed out waiting for data from DS18B20 sensor')

def _raw_read(file):
    with open(file) as f:
        return f.read().splitlines()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file',
                        required=True,
                        help='Path to 1-wire serial interface file')
    parser.add_argument('-F', '--fahrenheit',
                        action='store_const',
                        const=lambda x: '{:.1f}°F'.format(x * 9/5 + 32),
                        default=lambda x: '{:.1f}°C'.format(x),
                        dest='convert',
                        help='Convert results to deg F (default: deg C)')
    parser.add_argument('-t', '--timeout',
                        type=int,
                        metavar='N',
                        default=10,
                        help='Timeout after N seconds without a reading')
    parser.add_argument('-w', '--wait',
                        type=float,
                        metavar='N',
                        default=0.2,
                        help='Wait N seconds after failure before retrying')
    args = parser.parse_args()

    temp, _ = read(args.file)
    print('temp={}'.format(args.convert(temp)))
