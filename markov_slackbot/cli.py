# -*- coding: utf-8 -*-

import click

from markov_slackbot.main import markov_slackbot
from markov_slackbot.main import generate_example_config_file
from markov_slackbot.main import prepare_environment


def main():
    cli.add_command(run_bot)
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
def generate_example_config():
    """Generate an example config file."""
    generate_example_config_file()


@click.command()
def prepare_env():
    """Prepare the environment for the bot."""
    prepare_environment()


if __name__ == "__main__":
    main()
