# -*- coding: utf-8 -*-

from kafka import KafkaConsumer
from .publisher import Publisher
import os
import time
from kafka.errors import NoBrokersAvailable
from threading import Thread
import json
import random
import logging


TOPIC_SUB = 'streams_slave'
IP_KAFKA = os.environ.get('IP_KAFKA') or 'localhost'
PORT_KAFKA = os.environ.get('PORT_KAFKA') or '9092'
HEARTBEAT_S = 10  # period in second at which we check the producers


class ProducersOrchestrator():
    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        if len(self.logger.handlers) == 0:
            self.logger.addHandler(logging.StreamHandler())

        self._get_subscriber()
        self.dispatcher = Publisher()

        self.producers = {}  # uuid: info
        # producers = {'uuid1': ['streamer1', 'streamer2'],
        #              'uuid2': ['streamer3', 'streamer4', 'streamer5']}

        self.worker = Thread(target=self.run, args=())
        # setting threads as "daemon" allows main program to
        # exit eventually even if these dont finish
        # correctly.
        self.worker.setDaemon(True)
        self.worker.start()

    def _get_subscriber(self):
        while not hasattr(self, 'subscriber'):
            try:
                print(f'trying to connect to {IP_KAFKA}:{PORT_KAFKA}')
                self.subscriber = KafkaConsumer(
                    TOPIC_SUB,
                    bootstrap_servers=f'{IP_KAFKA}:{PORT_KAFKA}',
                    auto_offset_reset='latest',  # only receive messages sent after subscription
                    group_id=None,
                    enable_auto_commit=True)

            except NoBrokersAvailable as err:
                self.logger.error("Unable to find a broker: {0}".format(err))
                time.sleep(1)

    def run(self):
        # Should be launched as a thread
        while True:
            # Produce a broadcast message to all the producers
            self.logger.info('pushing broadcast')
            self.dispatcher.push(
                topic=TOPIC_SUB,
                key='broadcast')

            # Allow then to answer in 5 seconds
            time.sleep(5)
            raw_messages = self.subscriber.poll(timeout_ms=1000)

            self.producers = {}
            for topic_partition, messages in raw_messages.items():
                for msg in messages:
                    if msg.key == b'master':
                        # see producers/audiostreamers_manager.run()
                        data = json.loads(
                            msg.value.decode('utf-8'))
                        key, value = data['uuid'], data['streamers']
                        self.producers[key] = value
            time.sleep(5)

    def add(self, streamer_name: str):
        """
        Add a stream to the "chillest" (with the least streams) producer
        """
        min_number_of_streams = min(
            [len(v) for k, v in self.producers.items()])

        for k, v in self.producers.items():
            if len(v) == min_number_of_streams:
                chillest_producer = k
                break
        data = {'add': streamer_name}
        self.dispatcher.push(
            topic=TOPIC_SUB,
            key=chillest_producer,
            data=json.dumps(data).encode('utf-8'))
        self.producers[chillest_producer].append(streamer_name)

    def add_random(self, streamer_name: str):
        """
        Add a stream to a randomly picked procuder
        """
        producer = random.choice(self.producers.keys())
        data = {'add': streamer_name}
        self.dispatcher(
            topic=TOPIC_SUB,
            key=producer,
            data=json.dumps(data).encode('utf-8'))

    def get_streamers(self):
        return self.producers
