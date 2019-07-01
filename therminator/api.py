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
    logger.debug('Started posting data')

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
                time = response.elapsed.total_seconds()
                logger.info('Data posted to {}: {}'.format(endpoint, response.reason))
                logger.debug('Finished posting data ({:.1f}s)'.format(time))
            else:
                reason = response.reason
                message = response.json().get('error')
                logger.warning('Failed to post data to {}: {}: {}'.format(endpoint, reason, message))
            return
        except requests.exceptions.RequestException as e:
            logger.warning('Failed to post data: {!r}'.format(e))
            time.sleep(2)
    logger.error('Giving up after {} attempts'.format(retries))
