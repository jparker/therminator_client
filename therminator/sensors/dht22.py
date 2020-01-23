#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import time
import Adafruit_DHT as DHT

def read(pin, threshold=32, cache='/dev/shm/dht22', tolerance=5):
    """Return the external temperature and humidity.
    
    Keyword arguments:
    pin -- the GPIO pin connected to the DHT22's data pin
    """
    logger = logging.getLogger(__name__)

    ref = read_reference(cache, logger)
    logger.debug('Started reading sensor')
    t1 = time.time()
    humidity, temp = DHT.read_retry(DHT.DHT22, pin)
    write_reference(cache, temp, logger)
    if ref is not None and abs(temp - ref) > tolerance:
        logger.warning('reading offset exceeds {:.0f}C: retrying'.format(tolerance))
        logger.debug('last reading was {:.1f}C, new reading is {:.1f}C'.format(ref, temp))
        humidity, temp = DHT.read_retry(DHT.DHT22, pin)
        write_reference(cache, temp, logger)
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

def read_reference(cache, logger):
    if cache is not None:
        logger.debug('Read reference temperature from cache')
        try:
            with open(cache, 'r') as f:
                data = f.readline()
                return float(data)
        except FileNotFoundError:
            logger.warning('Reference cache file does not exist')
        except ValueError:
            logger.warning('Could not parse reference temeprature: {!r}'.format(data))

def write_reference(cache, ref, logger):
    if cache is not None:
        logger.debug('Write new reference temperature to cache')
        with open(cache, 'w+') as f:
            f.write('{:f}\n'.format(ref))


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
