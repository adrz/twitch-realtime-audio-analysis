# -*- coding: utf-8 -*-

import subprocess as sp
import time
from io import BytesIO
from threading import Thread

import logging

import streamlink
from pydub import AudioSegment
from pydub.exceptions import CouldntEncodeError
from .publisher import Publisher


logger = logging.getLogger()
logger.setLevel(logging.INFO)
if len(logger.handlers) == 0:
    logger.addHandler(logging.StreamHandler())


class AudioStreamer:
    def __init__(self, twitch_url: str, sampling_rate: int=16000,
                 window_size: int=20, daemon: bool=True):
        """
        Args:
            twitch_url: url of the stream
            sampling_rate: sampling rate in Hz
            window_size: length each window to be analysed
            daemon: True: non blocking, False: blocking
        """
        self.twitch_url = twitch_url
        self.streamer_name = self.twitch_url.split("/")[3]
        self.sampling_rate = sampling_rate
        self.window_size = window_size
        self.daemon = daemon
        self.is_running = True
        self.count_empty = 0
        self.dispatcher = Publisher()

        stream_works = self.create_pipe()

        if stream_works:
            self.start_buffer()

    def _stop(self):
        self.is_running = False

    def create_pipe(self):
        """
        Retrieve audio streams from the given twitch_url
        Launch ffmpeg to decode the audio stream as raw wave file and pipe it to
        a temporary buffer
        """
        try:
            streams = streamlink.streams(self.twitch_url)
        except streamlink.exceptions.NoPluginError:
            logger.info("No stream availabe for " + self.streamer_name)
            return False
        except:
            logger.info("No stream available no exception " + self.streamer_name)
            return False

        if 'audio_only' not in streams:
            logger.info("No audio stream available " + self.streamer_name)
            return
        stream = streams['audio_only']
        self.stream_url = stream.url

        self.pipe = sp.Popen(['ffmpeg',
                              '-i', self.stream_url,
                              '-f', 's16le',
                              "-loglevel", "quiet",
                              '-acodec', 'pcm_s16le',
                              '-ar', '{}'.format(self.sampling_rate),
                              '-ac', '1',
                              '-'], stdout=sp.PIPE, bufsize=10**8)

        return True

    def start_buffer(self):
        """
        Start a thread that will read the pipe
        """
        logger.info("starting stream: {}".format(self.streamer_name))
        self.t = Thread(target=self.update_buffer, args=())
        self.t.daemon = self.daemon
        self.t.start()
        return self

    def update_buffer(self):
        while True:
            if not self.is_running:
                return
            try:
                raw_audio = self.pipe.stdout.read(self.sampling_rate*2*self.window_size)
                # each frame is 2 bytes (16 bits)
                # so sampling_rate*2 is the number of sample for 1 second

            except:
                logger.error('ERROR pipe')
                continue

            # Check if the stream is empty (often the case when a stream has ended)
            if len(raw_audio) == 0:
                logger.info('empty stream for {}'.format(self.streamer_name))
                self.count_empty += 1
                if self.count_empty > 10:
                    self.is_running = False
                continue

            # Convert raw audio (wav format) into flac (required by google api)
            raw = BytesIO(raw_audio)
            try:
                raw_wav = AudioSegment.from_raw(
                    raw, sample_width=2, frame_rate=16000, channels=1)
            except CouldntEncodeError:
                logger.info('Could not encode: {}'.format(self.streamer_name))
                continue
            raw_flac = BytesIO()
            raw_wav.export(raw_flac, format='flac')
            t = time.time()
            data = raw_flac.read()
            self.dispatcher.push(key=self.streamer_name, audio=data)
