#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import requests
import time

def write(data, endpoint, api_key, timeout=30, retries=10):
    """Post data to API server.

    Keyword arguments:
    data -- dictionary of sensor readings to be posted
    endpoint -- URL of API endpoint for this sensor's readings
    api_key -- API account secret key
    """
    logger = logging.getLogger(__name__)
    logger.debug('Started posting data to {}'.format(endpoint))

    for i in range(1, retries+1):
        logger.debug('Attempt #{}'.format(i))
        try:
            response = requests.post(
                endpoint,
                headers={
                    'Authorization': api_key,
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                data=json.dumps(data),
                timeout=timeout,
            )
            if response.ok:
                elapsed_time = response.elapsed.total_seconds()
                logger.info('Data posted to server: {}'.format(response.reason))
                logger.debug('Finished posting data ({:.1f}s)'.format(elapsed_time))
            else:
                reason = response.reason
                message = response.json().get('error')
                logger.warning('Server failure: {}: {}'.format(reason, message))
            return
        except requests.exceptions.RequestException as e:
            logger.warning('Network failure: {!r}'.format(e))
            time.sleep(2)
    logger.error('Giving up after {} attempts'.format(retries))
