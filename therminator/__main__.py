#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from datetime import datetime
import logging
import logging.config
import os
import time
import yaml
from RPi import GPIO

from . import api
from .led import LED
from .sensors import *

LOCKFILE = '/var/tmp/therminator.lock'

SENSORS = {
    'pi': pi,
    'dht22': dht22,
    'ds18b20': ds18b20,
    'photoresistor': photoresistor,
}

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--config',
        metavar='FILE',
        required=True,
        help='Path to YAML config file'
    )
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Enable debugging output'
    )
    parser.add_argument(
        '-n', '--dry-run',
        action='store_true',
        help='Dry run -- do not post data to API'
    )
    return parser.parse_args()

def load_config(file):
    with open(file) as f:
        return yaml.safe_load(f)

def setup_logger(config, debug=False):
    logging.config.dictConfig(config)
    logging.captureWarnings(capture=True)
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    return logging.getLogger('therminator')

def lookup_sensor(name):
    return SENSORS[name]

def lock(logger, retries=120):
    logger.debug('Acquiring lock')
    for i in range(retries):
        try:
            with open(LOCKFILE, 'x') as f:
                f.write(str(os.getpid()))
            logger.debug('Lock ackquired')
            return
        except FileExistsError:
            time.sleep(1)
            continue
    logger.error('Failed to acquire lock')

def unlock(logger):
    try:
        logger.debug('Relinquishing lock')
        os.unlink(LOCKFILE)
        logger.debug('Relinquished lock')
    except OSError:
        logger.warning('No lock to reqlinquish')

def main():
    args = parse_args()
    config = load_config(args.config)
    logger = setup_logger(config['logging'], debug=args.debug)

    lock(logger=logger)
    GPIO.setmode(GPIO.BCM)

    try:
        led = LED(**config['led'])

        logger.debug('Starting therminator run')
        led.on()
        t1 = time.time()

        timestamp = datetime.utcnow()

        sensor = config['internal']['sensor']
        kwargs = config['internal']['options']
        int_temp = lookup_sensor(sensor).read(**kwargs)

        sensor = config['temperature']['sensor']
        kwargs = config['temperature']['options']
        ext_temp, humidity = lookup_sensor(sensor).read(**kwargs)

        if 'light' in config:
            sensor = config['light']['sensor']
            kwargs = config['light']['options']
            resistance = lookup_sensor(sensor).read(**kwargs)
        else:
            resistance = 0

        if not args.dry_run and 'api' in config:
            payload=dict(
                timestamp=timestamp.isoformat(),
                int_temp=int_temp,
                ext_temp=ext_temp,
                humidity=humidity,
                resistance=resistance,
            )
            api.write(payload, **config['api'])

        t2 = time.time()
        led.off()

        logger.info(
            'int_temp={:.1f}C'
            ' ext_temp={:.1f}C humidity={:.1f}%'
            ' resistance={:.1f}ohms'
            ' runtime={:.1f}s'
            .format(int_temp, ext_temp, humidity, resistance, t2-t1))
        logger.debug('Completed therminator run')
    finally:
        GPIO.cleanup()
        unlock(logger)

main()
