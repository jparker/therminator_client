#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import time
import Adafruit_DHT as DHT

def read(pin, threshold=32):
    """Return the external temperature and humidity.
    
    Keyword arguments:
    pin -- the GPIO pin connected to the DHT22's data pin
    """
    logger = logging.getLogger(__name__)
    logger.debug('Started reading sensor')
    t1 = time.time()
    humidity, temp = DHT.read_retry(DHT.DHT22, pin)
    t2 = time.time()
    if temp is None or humidity is None:
        raise RuntimeError('DHT22 sensor returned incomplete data')
    if temp > threshold:
        logger.warning(
            'temp {:.1f}C exceeds threshold {:.1f}C' \
            .format(temp, threshold)
        )
    logger.info('temp={:.1f}C humidity={:.1f}%'.format(temp, humidity))
    logger.debug('Finished reading sensor ({:.1f}s)'.format(t2-t1))
    return temp, humidity


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pin',
                        type=int,
                        required=True,
                        help='GPIO pin from which to read data')
    parser.add_argument('-F', '--fahrenheit',
                        action='store_const',
                        const=lambda x: '{:.1f}°F'.format(x * 9/5 + 32),
                        default=lambda x: '{:.1f}°C'.format(x),
                        dest='convert',
                        help='Convert results to deg F (default: deg C)')
    args = parser.parse_args()

    temp, humidity = read(args.pin)
    print('temp={} humidity={:.1f}%'.format(args.convert(temp), humidity))
