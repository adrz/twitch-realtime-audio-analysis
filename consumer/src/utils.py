# -*- coding: utf-8 -*-

import json


def get_curses(filename: str='curses.txt'):
    """
    credit:
    https://github.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/blob/master/en
    """
    with open(filename, 'r') as f:
        words = [line.rstrip() for line in f]
    return words


def any_words_in_sentence(words: list, sentence: list):
    if sentence is None:
        return False
    def word_in_sentence(word, sentence):
        return word in sentence
    sentence = sentence.lower()
    return any([word_in_sentence(word, sentence)
                for word in words])


def extract_transcript(resp: str):
    """
    Extract the first results from google api speech recognition
    """
    if 'result' not in resp:
        raise ValueError({'Error non valid response from api: {}'.format(resp)})
    for line in resp.split("\n"):
        try:
            line = json.loads(line)
            line = line['result'][0]['alternative'][0]['transcript']
            return line
        except:
            # no result
            continue
