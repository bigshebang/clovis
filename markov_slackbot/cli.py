# -*- coding: utf-8 -*-

import click

from main import markov_slackbot


@click.command()
@click.argument('config_file')
def main(config_file):
    """Console script for markov_slackbot"""
    markov_slackbot(config_file)


if __name__ == "__main__":
    main()
