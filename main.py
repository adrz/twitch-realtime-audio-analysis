# -*- coding: utf-8 -*-

import click
from src.realtime_audiostreamer import AudioStreamer

@click.command()
@click.option('--url', '-u', help='url of twitch stream')
def main(url):
    AudioStreamer(twitch_url=url, daemon=False)

if __name__ == '__main__':
    main()
