#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import requests

def write(data, endpoint, api_key, timeout=30):
    """Post data to API server.

    Keyword arguments:
    data -- dictionary of sensor readings to be posted
    endpoint -- URL of API endpoint for this sensor's readings
    api_key -- API account secret key
    """
    logger = logging.getLogger(__name__)
    logger.debug('Started posting data')
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
    except requests.exceptions.RequestException as e:
        logger.warning('Failed to post data: {!r}'.format(e))
