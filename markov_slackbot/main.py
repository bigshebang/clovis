# -*- coding: utf-8 -*-

import json

from markov_slackbot import MarkovSlackbot


def markov_slackbot(config_file):
    """
    """

    config = json.loads(open(config_file).read())
    print(config)

    markov_slackbot = MarkovSlackbot(config)
    markov_slackbot.start()
