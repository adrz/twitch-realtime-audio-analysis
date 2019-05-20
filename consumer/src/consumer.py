from kafka import KafkaConsumer, TopicPartition
from kafka.errors import NoBrokersAvailable
import logging
import json
import os
import time
from pymongo import MongoClient
import uuid
import requests
from .utils import extract_transcript, get_curses
from concurrent.futures import ThreadPoolExecutor



topic = os.environ.get('TOPIC') or 'twitch'
IP_KAFKA = os.environ.get('IP_KAFKA')
if IP_KAFKA == 'localhost':
    IP_KAFKA = 'kafka'
PORT_KAFKA = os.environ.get('PORT_KAFKA')
MONGODB_HOST = os.environ.get('MONGODB_HOST')
MONGODB_DB = os.environ.get('MONGODB_DB')
MONGODB_COLLECTION = os.environ.get('MONGODB_COLLECTION')


class ConnectionException(Exception):
    pass


class Reader():
    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.info("Initializing the consumer")
        self.logger.setLevel(logging.INFO)
        if len(self.logger.handlers) == 0:
            self.logger.addHandler(logging.StreamHandler())
        # self.client = MongoClient(MONGODB_HOST)
        # self.collection = self.client[MONGODB_DB][MONGODB_COLLECTION]
        while not hasattr(self, 'consumer'):
            self.logger.info("Getting the kafka consumer")
            try:
                print(f'trying to connect to {IP_KAFKA}:{PORT_KAFKA}')
                # self.consumer = KafkaConsumer(
                #     topic,
                #     bootstrap_servers=f'{IP_KAFKA}:{PORT_KAFKA}',
                #     auto_offset_reset='earliest',
                #     group_id='consumer',
                #     enable_auto_commit=True,
                #     value_deserializer=lambda x: self._deserializer(x))
                self.consumer = KafkaConsumer(
                    topic,
                    bootstrap_servers=f'{IP_KAFKA}:{PORT_KAFKA}',
                    auto_offset_reset='earliest',
                    group_id='consumer',
                    enable_auto_commit=True)

            except NoBrokersAvailable as err:
                self.logger.error("Unable to find a broker: {0}".format(err))
                time.sleep(1)

        self.logger.info("We have a consumer {0}".format(time.time()))
        self.logger.info("ok {0}".format(time.time()))

    def processing(self):
        self.logger.info("Reading stream: {0}".format(topic))
        try:
            if self.consumer:
                try:
                    with ThreadPoolExecutor(max_workers=20) as executor:
                        for msg in self.consumer:
                            executor.submit(self.api_speech, msg)
                            # self.logger.info('{}: {}'.format(msg['streamer_name'],
                            #                                  msg['transcript']))
                            # self.logger.info(msg.value)
                            # with open('audios/{}.txt'.format(uuid.uuid4()), 'w') as f:
                            #     f.write(str(msg.value))

                            # print(msg['streamer_name'])
                except StopIteration:
                    return None
            raise ConnectionException
        except AttributeError:
            self.logger.error(("Unable to retrieve the next message. "
                               "There is no consumer to read from."))
            raise ConnectionException

    @staticmethod
    def _deserializer(x):
        """ Deserializer function """
        return json.loads(x.decode('utf-8'))

    def api_speech(self, msg):
        headers = {
            'Content-Type': 'audio/x-flac; rate=16000;',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.77 Safari/535.7',
        }
        params = (
            ('client', 'chromium'),
            ('pFilter', '0'),
            ('lang', 'en'),
            ('key', 'AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw'),
        )
        response = requests.post('http://www.google.com/speech-api/v2/recognize',
                                 headers=headers, params=params, data=msg.value)
        transcript = extract_transcript(response.text)
        self.logger.info('{}: {}'.format(msg.key, transcript))
        return 
