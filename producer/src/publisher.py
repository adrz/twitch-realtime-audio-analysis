# -*- coding: utf-8 -*-

import json
import logging
import os
import time

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

TOPIC = os.environ.get('TOPIC') or 'twitch'
IP_KAFKA = os.environ.get('IP_KAFKA')
if IP_KAFKA == 'localhost':
    IP_KAFKA = 'kafka'
PORT_KAFKA = os.environ.get('PORT_KAFKA')


class Publisher:
    def __init__(self):
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        self.logger = logger

        while not hasattr(self, 'producer'):
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=[f'{IP_KAFKA}:{PORT_KAFKA}'])
            except NoBrokersAvailable as err:
                self.logger.error("Unable to find a broker: {0}".format(err))
                time.sleep(1)

    def push(self, key, audio):
        try:
            if self.producer:
                self.producer.send(TOPIC, key=key.encode('utf-8'), value=audio)
                self.producer.flush()
        except AttributeError:
            self.logger.error("Unable to send {0}. The producer does not exist.".format(key))
        return None
