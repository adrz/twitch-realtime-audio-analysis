# -*- coding: utf-8 -*-

import subprocess as sp
import time
import uuid
from io import BytesIO
from threading import Thread

import requests

import streamlink
from pydub import AudioSegment
from .utils import any_words_in_sentence, extract_transcript, get_curses

curses_words = get_curses('src/curses.txt')


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

        stream_works = self.create_pipe()

        if stream_works:
            self.start_buffer()

    def create_pipe(self):
        try:
            streams = streamlink.streams(self.twitch_url)
        except streamlink.exceptions.NoPluginError:
            print("No stream availabe for " + self.streamer_name)
            return False
        except:
            print("No stream available no exception " + self.streamer_name)
            return False

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
        t = Thread(target=self.update_buffer, args=())
        t.daemon = self.daemon
        t.start()
        return self

    def update_buffer(self):
        while True:
            raw_audio = self.pipe.stdout.read(self.sampling_rate*2*self.window_size)
            # each frame is 2 bytes (16 bits)
            # so sampling_rate*2 is the number of sample for 1 second

            if len(raw_audio) == 0:
                break

            # Convert raw audio (wav format) into flac (required by google api)
            raw = BytesIO(raw_audio)
            raw_wav = AudioSegment.from_raw(
                raw, sample_width=2, frame_rate=16000, channels=1)
            raw_flac = BytesIO()
            raw_wav.export(raw_flac, format='flac')

            # Call google API
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
            t = time.time()
            data = raw_flac.read()
            response = requests.post('http://www.google.com/speech-api/v2/recognize',
                                     headers=headers, params=params, data=data)
            transcript = extract_transcript(response.text)
            print('{}: {}'.format(self.streamer_name,
                                  transcript))
            if any_words_in_sentence(curses_words, transcript):
                with open('curses/{}.flac'.format(uuid.uuid4()), 'wb') as f:
                    f.write(data)
                print('GOT a curse!!!!!!!!!!!!!!')
            print(time.time()-t)


def test():
    from src.realtime_audiostreamer import AudioStreamer
    AudioStreamer(twitch_url='https://www.twitch.tv/dyrus')
    AudioStreamer(twitch_url='https://www.twitch.tv/greekgodx')
    AudioStreamer(twitch_url='https://www.twitch.tv/pimpcsgo')
    AudioStreamer(twitch_url='https://www.twitch.tv/zombiunicorn')
    AudioStreamer(twitch_url='https://www.twitch.tv/pokket')
    AudioStreamer(twitch_url='https://www.twitch.tv/m0xyy')
