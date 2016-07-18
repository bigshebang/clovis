# -*- coding: utf-8 -*-

import json

from markov_slackbot import MarkovSlackbot


def markov_slackbot(config_file):
    """API equivalent to using markov_slackbot at the command line.

    :param config_file: User configureation path file.
    """

    config = json.loads(open(config_file).read())
    print(config)

    markov_slackbot = MarkovSlackbot(config)
    markov_slackbot.start()
