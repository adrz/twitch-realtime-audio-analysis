# -*- coding: utf-8 -*-

import json
import logging
import os
import time

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable


IP_KAFKA = os.environ.get('IP_KAFKA') or 'localhost'
PORT_KAFKA = os.environ.get('PORT_KAFKA') or '9092'


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

    def push(self, topic, key=None, data=b''):
        try:
            if self.producer:
                if key is not None:
                    self.producer.send(topic, key=key.encode('utf-8'), value=data)
                else:
                    self.producer.send(topic, value=data)
                self.producer.flush()
        except AttributeError:
            self.logger.error("Unable to send {0}. The producer does not exist.".format(key))
        return None
