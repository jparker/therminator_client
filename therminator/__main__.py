#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import logging.config
import time
import yaml
from RPi import GPIO

from . import __version__, SENSORS
from .led import LED

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
        '-v', '--version',
        action='store_true',
        help='Display version information and exit'
    )
    return parser.parse_args()

def display_version_and_exit():
    print('therminator-client {}'.format(__version__))
    exit()

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

def main():
    args = parse_args()
    if args.version:
        display_version_and_exit()
    config = load_config(args.config)
    logger = setup_logger(config['logging'], debug=args.debug)

    GPIO.setmode(GPIO.BCM)

    try:
        led = LED(**config['led'])

        logger.debug('Starting therminator run')
        led.on()
        t1 = time.time()

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

main()
