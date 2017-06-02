#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import requests

def write(data, endpoint, api_key):
    """Post data to API server.

    Keyword arguments:
    data -- dictionary of sensor readings to be posted
    endpoint -- URL of API endpoint for this sensor's readings
    api_key -- API account secret key
    """
    logger = logging.getLogger(__name__)
    logger.debug('Started posting data')
    response = requests.post(
        endpoint,
        headers={
            'Authorization': api_key,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
        data=json.dumps(data),
    )
    if response.ok:
        time = response.elapsed.total_seconds()
        logger.info('Data posted to API: {}'.format(response.reason))
        logger.debug('Finished posting data ({:.1f}s)'.format(time))
    else:
        reason = response.reason
        message = response.json().get('error')
        logger.warning('Failed to post data: {}: {}'.format(reason, message))
