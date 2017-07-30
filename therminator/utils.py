#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import logging.config
import os
import time
import yaml

from .led import LED, NullLED
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
        help='Path to YAML-formatted config file',
    )
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Enable debug output',
    )
    parser.add_argument(
        '-n', '--dry-run',
        action='store_true',
        help='Dry run -- do not post data to API',
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
            logger.debug('Lock acquired')
            return
        except FileExistsError:
            time.sleep(1)
            continue
    logger.error('Failed to acquire lock')

def unlock(logger):
    try:
        logger.debug('Relinquishing lock')
        os.unlink(LOCKFILE)
        logger.debug('Lock relinquished')
    except OSError:
        logger.warning('No lock to relinquish')
