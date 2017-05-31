#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import re
import time

def read(file='/sys/class/thermal/thermal_zone0/temp'):
    """Return the internal temperature.

    Keyword arguments:
    file -- path to kernal interface file for internal temperature

    The default value for file, /sys/class/thermal/thermal_zone0/temp, is a
    safe bet for a device as simple as a Raspberry Pi. On a device with
    multiple internal temperature zones, you can consult the type file in the
    same directory to identify the correct zone.
    """
    logger = logging.getLogger(__name__)
    logger.debug('Started reading sensor')
    t1 = time.time()
    with open(file) as f:
        temp = float(f.read()) / 1000
    t2 = time.time()
    logger.info('int_temp={:.1f}C'.format(temp))
    logger.debug('Finished reading sensor ({:.1f}s)'.format(t2-t1))
    return temp


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-F', '--fahrenheit',
                        action='store_const',
                        const=lambda x: '{:.1f}°F'.format(x * 9/5 + 32),
                        default=lambda x: '{:.1f}°C'.format(x),
                        dest='convert',
                        help='Convert results to °F (default: °C)')
    parser.add_argument('-f', '--file',
                        default='/sys/class/thermal/thermal_zone0/temp',
                        help='Path to kernel interface to CPU temperature' \
                             ' (default: /sys/class/thermal/thermal_zone0/temp)')
    args = parser.parse_args()

    temp = read(args.file)
    print('temp={}'.format(args.convert(temp)))
