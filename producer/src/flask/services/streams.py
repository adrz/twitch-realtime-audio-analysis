from flask import g
from src.realtime_audiostreamer import AudioStreamer

def get_streams():
    if "streams" not in g:
        g.streams = {}

    return g.streams

def get_streamers():
    streams = get_streams()
    return list(streams.keys())

def add_streamer(stream_name: str):
    stream_url = get_stream_url(stream_name)
    streams = get_streams()
    if stream_name not in streams:
        streams[stream_name] = AudioStreamer(twitch_url=stream_url,
                                            window_size=10,
                                            daemon=False)

def remove_streamer(stream_name: str):
    streams = get_streams()
    if stream_name in streams:
        streams[stream_name]._stop()
        del streams[stream_name]

def get_stream_url(stream_name: str):
    return f'https://www.twitch.tv/{stream_name}'