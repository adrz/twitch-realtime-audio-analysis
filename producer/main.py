# -*- coding: utf-8 -*-

import click
from src.realtime_audiostreamer import AudioStreamer


@click.command()
@click.option('--url', '-u', help='url of twitch stream')
@click.option('--length', '-l', type=int, default=20, help='window size in sec')
def main(url, length):
    AudioStreamer(twitch_url=url, window_size=length, daemon=False)


if __name__ == '__main__':
    main()
