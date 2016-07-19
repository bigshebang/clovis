# -*- coding: utf-8 -*-

import json
import pandas as pd
from os import path, makedirs, walk

from markov_slackbot.markov_slackbot import MarkovSlackbot
from markov_slackbot.data_clean import parse_slack_json


def markov_slackbot(config_file):
    """API equivalent to using markov_slackbot at the command line.

    :param config_file: User configuration path file.
    """

    config = json.loads(open(config_file).read())

    markov_slackbot = MarkovSlackbot(config)
    markov_slackbot.start()


def clean_raw_slack_json(raw_filepath, clean_filepath):
    """Clean raw Slack data from raw_filepath and write it to clean_filepath.

    :param raw_filepath: Raw Slack data file
    :param clean_filepath: Clean Slack data file
    """

    raw_file_json = pd.read_json(raw_filepath)
    clean_data = parse_slack_json(raw_file_json)

    clean_data_file = open(clean_filepath, 'a')
    clean_data_file.seek(0)
    clean_data_file.truncate()

    clean_data_file.write(clean_data)


def clean_raw_slack_dir(raw_dir, clean_dir):
    """Clean Slack log directory, outputting a new directory with preserved
    structure.

    :param raw_dir: The directory of raw slack logs.
    :param clean_dir: The directory to write cleaned logs to.
    """

    if not path.exists(clean_dir):
        makedirs(clean_dir)

    # Do a recursive walk over the raw directory
    for root, subdirs, files in walk(raw_dir):
        # Create subdirectories in the clean directory
        for subdir in subdirs:
            clean_subdir = path.join(clean_dir, subdir)
            if not path.exists(clean_subdir):
                makedirs(clean_subdir)

        for raw_filename in files:
            raw_filepath = path.join(root, raw_filename)

            # Creating the new root by replacing the first part of the path
            clean_root = root.replace(raw_dir, clean_dir, 1)

            clean_filename = raw_filename.replace('.json', '.txt')
            clean_filepath = path.join(clean_root, clean_filename)

            clean_raw_slack_json(raw_filepath, clean_filepath)


def generate_example_config_file():
    """Create an example config file.
    """

    example_config = {
        'SLACK_TOKEN': 'your token here',
        'raw_chatlog_dir': 'raw_logs',
        'clean_chatlog_dir': 'clean_logs',
        'mixin_dir': 'mixins'
    }

    example_config_json = json.dumps(example_config, sort_keys=True, indent=4)

    example_config_file = open('config.json.example', 'a')
    example_config_file.seek(0)
    example_config_file.truncate()
    example_config_file.write(example_config_json)


def prepare_environment():
    """Prepare the environment for the bot.
    """

    if not path.exists('raw_logs'):
        makedirs('raw_logs')

    if not path.exists('mixins'):
        makedirs('mixins')

    if not path.exists('clean_logs'):
        makedirs('clean_logs')

    generate_example_config_file()
