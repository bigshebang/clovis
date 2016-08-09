# -*- coding: utf-8 -*-

import json
from os import path, makedirs, walk

from markov_slackbot.markov_slackbot import MarkovSlackbot


def markov_slackbot(config_file):
    """API equivalent to using markov_slackbot at the command line.

    :param config_file: User configuration path file.
    """

    config = json.loads(open(config_file).read())

    markov_slackbot = MarkovSlackbot(config)
    markov_slackbot.start()


def generate_example_config_file():
    """Create an example config file.
    """

    example_config = {
        'SLACK_TOKEN': 'your token here',
        'slack_log_dir': 'slack_logs',
        'clean_chatlog_dir': 'clean_logs',
        'external_text_dir': 'external_texts',
        'send_mentions': False
    }

    example_config_json = json.dumps(example_config, sort_keys=True, indent=4)

    example_config_file = open('config.json.example', 'a')
    example_config_file.seek(0)
    example_config_file.truncate()
    example_config_file.write(example_config_json)


def prepare_environment():
    """Prepare the environment for the bot.
    """

    if not path.exists('slack_logs'):
        makedirs('slack_logs')

    if not path.exists('external_texts'):
        makedirs('external_texts')

    generate_example_config_file()
