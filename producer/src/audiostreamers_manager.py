# -*- coding: utf-8 -*-

from .audiostreamer import AudioStreamer


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

    def get_streamers(self):
        """ Return currently monitored streamer names """
        return list(self.streams.keys())

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
