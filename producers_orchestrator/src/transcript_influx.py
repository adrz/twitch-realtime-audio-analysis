# -*- coding: utf-8 -*-

import os
from influxdb import InfluxDBClient
import time
import logging

INFLUXDB_HOST = os.environ.get('INFLUXDB_HOST') or 'localhost'
INFLUXDB_PORT = os.environ.get('INFLUXDB_PORT') or '8086'
INFLUXDB_USER = os.environ.get('INFLUXDB_USER') or 'root'
INFLUXDB_PASS = os.environ.get('INFLUXDB_PASS') or 'root'
INFLUXDB_DB = os.environ.get('INFLUXDB_DB') or 'twitch'
INFLUXDB_MEASUREMENT = os.environ.get('INFLUXDB_MEASUREMENT') or 'twitch_transcript'


class TranscriptGetter(object):
    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.info("Initializing the consumer")
        self.logger.setLevel(logging.INFO)

        # InfluxDB
        while not hasattr(self, 'influx_client'):
            self.logger.info('Getting influxdb client')
            try:
                self.influx_client = InfluxDBClient(
                    INFLUXDB_HOST, int(INFLUXDB_PORT),
                    INFLUXDB_USER, INFLUXDB_PASS,
                    INFLUXDB_DB)
            except:
                self.logger.error('Unable to find influxdb')
                time.sleep(1)

    def get_transcript(self, streamer_name: str) -> list:
        query = ('SELECT transcript, streamer_name '
                 'from {} where time > now()-15m;').format(INFLUXDB_MEASUREMENT)
        rs = self.influx_client.query(query)
        return list(rs)
