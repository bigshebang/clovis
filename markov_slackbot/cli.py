# -*- coding: utf-8 -*-

import click

from main import markov_slackbot
from main import clean_raw_slack_json
from main import clean_raw_slack_dir
from main import generate_example_config_file


@click.group()
def main():
    pass


@click.command()
@click.argument('config_file')
def run_bot(config_file):
    """Start the bot."""
    markov_slackbot(config_file)


@click.command()
@click.argument('raw_filepath')
@click.argument('clean_filepath')
def clean_file(raw_filepath, clean_filepath):
    """Clean a raw slack logfile."""
    clean_raw_slack_json(raw_filepath, clean_filepath)


@click.command()
@click.argument('raw_dir_name')
@click.argument('clean_dir_name')
def clean_dir(raw_dir_name, clean_dir_name):
    """Clean a directory of raw slack logfiles."""
    clean_raw_slack_dir(raw_dir_name, clean_dir_name)


@click.command()
def generate_example_config():
    """Generate an example config file."""
    generate_example_config_file()


if __name__ == "__main__":
    main.add_command(run_bot)
    main.add_command(clean_file)
    main.add_command(clean_dir)
    main.add_command(generate_example_config)
    main()
