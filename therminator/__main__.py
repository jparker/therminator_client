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
from .led import LED, NullLED
from .sensors import *
from .utils import *

def main():
    args = parse_args()
    config = load_config(args.config)
    logger = setup_logger(config['logging'], debug=args.debug)

    lock(logger=logger)
    GPIO.setmode(GPIO.BCM)

    try:
        if 'led' in config:
            led = LED(**config['led'])
        else:
            led = NullLED()

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

        t2 = time.time()
        led.off()

        log_message = 'timestamp={}'.format(timestamp.isoformat())
        log_message += ' int_temp={:f}C'.format(int_temp)
        log_message += ' ext_temp={:f}C'.format(ext_temp)
        if humidity is not None:
            log_message += ' humidity={:f}%'.format(humidity)
        log_message += ' resistance={:f}ohms'.format(resistance)
        log_message += ' runtime={:.1f}s'.format(t2-t1)
        logger.info(log_message)
    finally:
        GPIO.cleanup()
        unlock(logger)

    if not args.dry_run and 'api' in config:
        payload = dict(
            timestamp=timestamp.isoformat(),
            int_temp=int_temp,
            ext_temp=ext_temp,
            humidity=humidity,
            resistance=resistance,
        )
        api.write(payload, **config['api'])

    logger.debug('Completed therminator run')

main()
