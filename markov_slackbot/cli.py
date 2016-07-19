# -*- coding: utf-8 -*-

import click

from markov_slackbot.main import markov_slackbot
from markov_slackbot.main import clean_raw_slack_json
from markov_slackbot.main import clean_raw_slack_dir
from markov_slackbot.main import generate_example_config_file
from markov_slackbot.main import prepare_environment


def main():
    cli.add_command(run_bot)
    cli.add_command(clean_file)
    cli.add_command(clean_dir)
    cli.add_command(generate_example_config)
    cli.add_command(prepare_env)
    cli()


@click.group()
def cli():
    pass


@click.command()
@click.option('--config_file', default='config.json',
              help='Configuration filepath.')
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
@click.option('--raw_dir_name', default='raw_logs', help='Raw log directory.')
@click.option('--clean_dir_name', default='clean_logs',
              help='Clean log directory')
def clean_dir(raw_dir_name, clean_dir_name):
    """Clean a directory of raw slack logfiles."""
    clean_raw_slack_dir(raw_dir_name, clean_dir_name)


@click.command()
def generate_example_config():
    """Generate an example config file."""
    generate_example_config_file()


@click.command()
def prepare_env():
    """Prepare the environment for the bot."""
    prepare_environment()


if __name__ == "__main__":
    main()
