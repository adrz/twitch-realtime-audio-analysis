# -*- coding: utf-8 -*-

import subprocess as sp
import time
import uuid
from io import BytesIO
from threading import Thread

import requests
import logging

import streamlink
from pydub import AudioSegment
from .utils import any_words_in_sentence, extract_transcript, get_curses
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
        self.dispatcher = Publisher()

        stream_works = self.create_pipe()

        if stream_works:
            self.start_buffer()

    def _stop(self):
        self.is_running = False

    def create_pipe(self):
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
            except:
                logger.error('ERROR pipe')
            # each frame is 2 bytes (16 bits)
            # so sampling_rate*2 is the number of sample for 1 second

            if len(raw_audio) == 0:
                logger.info('empty stream for {}'.format(self.streamer_name))

            # Convert raw audio (wav format) into flac (required by google api)
            raw = BytesIO(raw_audio)
            logger.info('new sample from {}'.format(self.streamer_name))
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


def test():
    from src.realtime_audiostreamer import AudioStreamer
    from twitch.api import streams

    streams = (streams.Streams(client_id='fqsudq063tmmzfbypb3d9xophrk3jk')
               .get_live_streams(limit=50))
    for stream in streams:
        print('{}: {}'.format(stream.channel.url,
                              stream.viewers))

    audios = []
    for stream in streams:
        audios.append(AudioStreamer(twitch_url=stream.channel.url))

    # v = AudioStreamer(twitch_url=streams[0].channel.url)
    # AudioStreamer(twitch_url='https://www.twitch.tv/greekgodx')
    # AudioStreamer(twitch_url='https://www.twitch.tv/pimpcsgo')
    # AudioStreamer(twitch_url='https://www.twitch.tv/zombiunicorn')
    # AudioStreamer(twitch_url='https://www.twitch.tv/pokket')
    # AudioStreamer(twitch_url='https://www.twitch.tv/m0xyy')


def test_async():
    import aiohttp
    import asyncio
    from bs4 import BeautifulSoup
    import requests
    n_sample = 20

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.77 Safari/535.7'}
    async def fetch(session, url):
        async with session.get(url, proxy='http://127.0.0.1:5566', headers=headers) as response:
            return await response.text()

    async def main():
        async with aiohttp.ClientSession() as session:
            for i in range(n_sample):
                html = await fetch(session, 'http://www.monip.org/')
                soup = BeautifulSoup(html)
                print(soup.find('font').text)

    loop = asyncio.get_event_loop()
    t = time.time()
    main()
    loop.run_forever()
    loop.run_until_complete(main())
    print(time.time()-t)

    t = time.time()
    for i in range(n_sample):
        r = requests.get('http://www.monip.org/',
                         proxies={'http': '127.0.0.1:5566'})
        soup = BeautifulSoup(r.text)
        print(soup.find('font').text)

    print(time.time()-t)


    from requests_threads import AsyncSession
    import time
    session = AsyncSession(n=10)

    async def _main():
        for _ in range(20):
            rs.append(await session.get('http://httpbin.org/get'))
        print(rs)

    session.run(_main())


    from threading import Thread
    import requests
    import time
    def get_request(url):
        r = requests.get(url)
        print(r.text)
        return

    # tt = time.time()
    # threads = []
    # for i in range(200):
    #     t = Thread(target=get_request, args=())
    #     t.daemon = True
    #     t.start()
    #     threads.append(t)

    # [t.join() for t in threads]
    # print(time.time()-tt)
    from concurrent.futures import ThreadPoolExecutor
    
    tt = time.time()
    url = 'http://httpbin.org/get'
    with ThreadPoolExecutor(max_workers=20) as executor:
        for i in range(200):
            if i%10 == 0:
                time.sleep(3)
            executor.submit(get_request, url)
            # r = get_request()
    print(time.time()-tt)
