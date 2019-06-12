# -*- coding: utf-8 -*-

import logging
import os
import time

from flask_restplus import Namespace, Resource, fields, reqparse
from influxdb import InfluxDBClient

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

    def get_transcript(self, streamer_name: str, duration: str) -> list:
        query = ('SELECT transcript, streamer_name '
                 'from {} where time > now()-{};').format(INFLUXDB_MEASUREMENT,
                                                          duration)
        logger.info(query)
        rs = self.influx_client.query(query)
        return list(rs)

    def get_n_words(self, streamer_name: str, duration: str,
                    frequency: str, field='n_words') -> list:
        query = ('SELECT sum({field}) from {measurement} '
                 'WHERE time > now()-{duration} '
                 'GROUP BY time({frequency});').format(measurement=INFLUXDB_MEASUREMENT,
                                                       duration=duration,
                                                       frequency=frequency,
                                                       field=field)
        logger.info(query)
        rs = self.influx_client.query(query)
        return list(rs)


transcript_getter = TranscriptGetter()


api = Namespace('transcript', description='Transcript API')

my_fields_raw = api.model('raw', {
    'streamer_name': fields.String(required=True, description='username of the streamer'),
    'duration': fields.String(required=True,
                              description=('control the duration of transcript to retrieve, '
                                           'data from now()-duration will be returned. '
                                           'Should be of the format Xm (minutes), '
                                           'Xh (hours), Xd (days)'))})

my_fields_words = api.model('count_words', {
    'streamer_name': fields.String(required=True, description='username of the streamer'),
    'duration': fields.String(required=True,
                              description=('control the duration of transcript to retrieve, '
                                           'data from now()-duration will be returned. '
                                           'Should be of the format Xm (minutes), '
                                           'Xh (hours), Xd (days)')),
    'frequency': fields.String(required=False,
                               description=('countrol the frequency of groupby, '
                                            'Should be of the format Xm (minutes), '
                                            'Xh (hours), Xd (days)'))})

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if len(logger.handlers) == 0:
    logger.addHandler(logging.StreamHandler())


@api.route('/raw')
class Transcript(Resource):
    @api.doc('post_data')
    @api.expect(my_fields_raw)
    # @api.marshal_with(my_fields_raw, code=201)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('streamer_name', type=str)
        parser.add_argument('duration', type=str)
        args = parser.parse_args()
        data = transcript_getter.get_transcript(args['streamer_name'],
                                                args['duration'])
        logger.info(data)
        return data, 200


@api.route('/count_words')
class Words(Resource):
    @api.doc('post_words')
    @api.expect(my_fields_words)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('streamer_name', type=str)
        parser.add_argument('duration', type=str)
        parser.add_argument('frequency', type=str)
        args = parser.parse_args()
        data = transcript_getter.get_n_words(args['streamer_name'],
                                             args['duration'],
                                             args['frequency'],
                                             'n_words')
        return data, 200


@api.route('/count_swears')
class Swears(Resource):
    @api.doc('post_words')
    @api.expect(my_fields_words)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('streamer_name', type=str)
        parser.add_argument('duration', type=str)
        parser.add_argument('frequency', type=str)
        args = parser.parse_args()
        data = transcript_getter.get_n_words(args['streamer_name'],
                                             args['duration'],
                                             args['frequency'],
                                             'has_curse')
        return data, 200
