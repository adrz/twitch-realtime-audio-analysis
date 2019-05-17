from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import json
import os
import time
import logging

topic = os.environ.get('TOPIC') or 'stats'
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
                    bootstrap_servers=[f'{IP_KAFKA}:{PORT_KAFKA}'],
                    value_serializer=lambda x: json.dumps(x).encode('utf-8'))
            except NoBrokersAvailable as err:
                self.logger.error("Unable to find a broker: {0}".format(err))
                time.sleep(1)

    def push(self, message):
        self.logger.debug("Publishing: {0}".format(message))
        try:
            if self.producer:
                self.producer.send('stats', value=message)
                self.producer.flush()
        except AttributeError:
            self.logger.error("Unable to send {0}. The producer does not exist.".format(message))
        return None

