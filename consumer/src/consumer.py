from kafka import KafkaConsumer, TopicPartition
from kafka.errors import NoBrokersAvailable
import logging
import json
import os
import time
from pymongo import MongoClient
import uuid
import requests
from .utils import extract_transcript, get_curses, any_words_in_sentence
from concurrent.futures import ThreadPoolExecutor
import random
import datetime


topic = os.environ.get('TOPIC') or 'twitch'
IP_KAFKA = os.environ.get('IP_KAFKA')
if IP_KAFKA == 'localhost':
    IP_KAFKA = 'kafka'
PORT_KAFKA = os.environ.get('PORT_KAFKA')
MONGODB_HOST = os.environ.get('MONGODB_HOST')
MONGODB_DB = os.environ.get('MONGODB_DB')
MONGODB_COLLECTION = os.environ.get('MONGODB_COLLECTION')
PROXY = os.environ.get('PROXY')

curses_words = get_curses('src/curses.txt')

class ConnectionException(Exception):
    pass

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

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
                    with ThreadPoolExecutor(max_workers=5) as executor:
                        for msg in self.consumer:
                            executor.submit(self.api_speech, msg)
                    # for msg in self.consumer:
                    #     try:
                    #         self.api_speech(msg)
                    #     except Exception as inst:
                    #         self.logger.error('ERROR api_speech', exc_info=True)
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
        data = msg.value
        proxies = {'http': PROXY,
                   'https': PROXY}
        # proxies = None
        if len(data) == 0:
            return
        try:
            response = requests.post('http://www.google.com/speech-api/v2/recognize',
                                     proxies=proxies,
                                     headers=headers, params=params, data=data)
        except Exception as inst:
            self.logger.error('ERROR requests', exc_info=True)

        try:
            transcript = extract_transcript(response.text)
        except Exception as inst:
            self.logger.error('ERROR transcript', exc_info=True)
            return

        date = datetime.datetime.fromtimestamp(int(msg.timestamp)//1000)
        self.logger.info('{}, {}: {}'.format(date.strftime('%Y-%m-%dT%H:%M:%S'),
                                                 msg.key, transcript))
        filename = 'audios/curses/{}.flac'.format(uuid.uuid4())
        has_curse = any_words_in_sentence(curses_words, transcript)

        if has_curse:
            try:
                with open(filename, 'wb') as f:
                    f.write(data)
            except Exception as inst:
                self.logger.error('ERROR: {}'.format(inst))
            finally:
                self.logger.info('Curse saved')
        if random.random() < .03:
            if transcript is not None:
                filename_detect_sound = 'audios/voice/{}.flac'.format(uuid.uuid4())
                try:
                    with open(filename_detect_sound, 'wb') as f:
                        f.write(data)
                except Exception as inst:
                    self.logger.error('ERROR random', exc_info=True)
            else:
                filename_detect_sound = 'audios/novoice/{}.flac'.format(uuid.uuid4())
                try:
                    with open(filename_detect_sound, 'wb') as f:
                        f.write(data)
                except Exception as inst:
                    self.logger.error('ERROR random', exc_info=True)

        if transcript is not None:
            dict_mongo = {'timestamp': msg.timestamp,
                          'transcript': transcript,
                          'streamer_name': msg.key.decode('utf-8'),
                          'filename': filename if has_curse else None}
            try:
                with MongoClient(MONGODB_HOST) as client:
                    db = client[MONGODB_DB]
                    collection = db[MONGODB_COLLECTION]
                    collection.insert_one(dict_mongo)
            except Exception as inst:
                self.logger.error('ERROR mongo', exc_info=True)
        return 
