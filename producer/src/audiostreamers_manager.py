# -*- coding: utf-8 -*-

from .audiostreamer import AudioStreamer
from kafka import KafkaConsumer
import uuid
import os
import time
from kafka.errors import NoBrokersAvailable
from threading import Thread
import json
from .publisher import Publisher
import logging


TOPIC_SUB = 'streams_slave'
TOPIC_PUB = 'streams_master'
IP_KAFKA = os.environ.get('IP_KAFKA') or 'localhost'
PORT_KAFKA = os.environ.get('PORT_KAFKA') or '9092'


class AudioStreamersManager():
    """
    Threads Manager for AudioStreamer.
    It allows to start/stop recording of streams.

    TODO:
        - check if stream exists: _check_stream
        - return error if no stream or if streamer already monitored

        - the manager should also produce a message through kafka to
        warn when a stream die
    """

    def __init__(self):
        self.streams = {}
        self.uuid = str(uuid.uuid4()).encode('utf-8')
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        if len(self.logger.handlers) == 0:
            self.logger.addHandler(logging.StreamHandler())

        self._get_subscriber()
        self.dispatcher = Publisher()
        # logging.debug('Starting thread ', i)
        self.worker = Thread(target=self.run, args=())
        # setting threads as "daemon" allows main program to
        # exit eventually even if these dont finish
        # correctly.
        self.worker.setDaemon(False)
        self.worker.start()

    def run(self):
        """
        Thread running in background and wait for a message from kafka to trigger actions
        """
        self.logger.info('starting')
        while True:
            for msg in self.subscriber:
                key = msg.key
                if key == self.uuid:
                    message = json.loads(msg.value.decode('utf-8'))
                    if 'add' in message:
                        self.add_streamer(message['add'])
                    if 'del' in message:
                        self.remove_streamer(message['del'])
                if key == b'broadcast':
                    self.logger.info('receiving broadcast')
                    streamers_state = self.get_streamers_alive()
                    payload = {'uuid': self.uuid.decode('utf-8'),
                               'streamers': streamers_state}
                    self.logger.info('payload: {}'.format(payload))
                    self.dispatcher.push(topic=TOPIC_SUB,
                                         key='master',
                                         data=json.dumps(payload).encode('utf-8'))

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

    def get_streamers(self):
        """ Return currently monitored streamer names """
        return list(self.streams.keys())

    def get_streamers_alive(self):
        """
        Return the current state (running or not) of each threads managed.
        """
        state = [key for key in self.streams
                 if self.streams[key].is_running]
        return state

    def add_streamer(self, stream_name: str):
        stream_url = self._get_stream_url(stream_name)

        # Error handling for bad stream_name
        # TODO
        if stream_url is None:
            return None

        if stream_name not in self.streams:
            self.streams[stream_name] = AudioStreamer(twitch_url=stream_url,
                                                      window_size=10,
                                                      daemon=False)

    def remove_streamer(self, stream_name: str):
        if stream_name in self.streams:
            self.streams[stream_name].stop()
            del self.streams[stream_name]

    def _get_stream_url(self, stream_name: str):
        return f'https://www.twitch.tv/{stream_name}'

    def _check_stream(self, url: str):
        raise NotImplementedError()
