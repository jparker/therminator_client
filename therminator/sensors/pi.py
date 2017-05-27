#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import re
import time
from subprocess import Popen, PIPE

def read():
    """Return the CPU and GPU temperatures."""
    logger = logging.getLogger(__name__)
    logger.debug('Started reading sensor')
    t1 = time.time()
    cpu, gpu = cpu_temp(), gpu_temp()
    time.sleep(0.5)
    t2 = time.time()
    logger.info('cpu_temp={:.1f}C gpu_temp={:.1f}C'.format(cpu, gpu))
    logger.debug('Finished reading sensor ({:.1f}s)'.format(t2-t1))
    return cpu, gpu

def cpu_temp():
    """Return the CPU temperature."""
    with open('/sys/class/thermal/thermal_zone0/temp') as f:
        return float(f.read()) / 1000

def gpu_temp():
    """Return the GPU temperature."""
    with Popen(['vcgencmd', 'measure_temp'], stdout=PIPE) as p:
        data = p.stdout.read().decode()
        return float(re.search(r"=(\d+(?:\.\d+)?)'", data).group(1))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-F', '--fahrenheit',
                        action='store_const',
                        const=lambda x: '{:.1f}°F'.format(x * 9/5 + 32),
                        default=lambda x: '{:.1f}°C'.format(x),
                        dest='convert',
                        help='Convert results to °F (default: °C)')
    args = parser.parse_args()

    cpu, gpu = read()
    print('cpu={} gpu={}'.format(*map(args.convert, read())))
