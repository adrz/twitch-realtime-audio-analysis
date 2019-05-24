# -*- coding: utf-8 -*-


import logging
import time

from src.realtime_audiostreamer import AudioStreamer
from twitch.api import streams


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if len(logger.handlers) == 0:
        logger.addHandler(logging.StreamHandler())
    logger.info('sleeping for 5 minutes before launching')
    time.sleep(4*1)
    logger.info('end of sleep')
    streams_list = (streams.Streams(client_id='fqsudq063tmmzfbypb3d9xophrk3jk')
                    .get_live_streams(limit=50, language='en'))
    for stream in streams_list:
        print('{}: {}'.format(stream.channel.url,
                              stream.viewers))

    audios = {}
    for stream in streams_list:
        try:
            audios[stream.channel.url] = AudioStreamer(twitch_url=stream.channel.url,
                                                       window_size=10, daemon=False)
        except:
            continue

    while True:
        time.sleep(10)
        for key in audios:
            try:
                is_alive = audios[key].t.isAlive()
            except:
                continue
            if is_alive:
                logger.error('{}: is alive'.format(key))
            else:
                logger.error('{}: is DEAD'.format(key))
    # AudioStreamer(twitch_url='https://www.twitch.tv/ninja',
    #               window_size=10, daemon=False)
    # AudioStreamer(twitch_url='https://www.twitch.tv/seriousgaming',
    #               window_size=10, daemon=False)
    # AudioStreamer(twitch_url='https://www.twitch.tv/miss_angeliquew',
    #               window_size=10, daemon=False)
    # AudioStreamer(twitch_url='https://www.twitch.tv/babyhsu888',
    #               window_size=10, daemon=False)
    # AudioStreamer(twitch_url='https://www.twitch.tv/allkeyshop_tv',
    #               window_size=10, daemon=False)
    # AudioStreamer(twitch_url='https://www.twitch.tv/zumi',
    #               window_size=10, daemon=False)
    # AudioStreamer(twitch_url='https://www.twitch.tv/yunicorn19',
    #               window_size=10, daemon=False)
    # AudioStreamer(twitch_url='https://www.twitch.tv/bobbypoffgaming',
    #               window_size=10, daemon=False)
    # AudioStreamer(twitch_url='https://www.twitch.tv/hellomeganlee',
    #               window_size=10, daemon=False)
    # AudioStreamer(twitch_url='https://www.twitch.tv/sttasha',
    #               window_size=10, daemon=False)
