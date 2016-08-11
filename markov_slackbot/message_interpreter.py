# -*- coding: utf-8 -*-

from itertools import chain
import logging
import re


class MessageInterpreter(object):
    def __init__(self, user_id, username, command_names, external_texts):
        self.logger = logging.getLogger(__name__)
        self.user_id = user_id
        self.username = username
        self.external_texts = external_texts
        self.command_regexes = self.compile_command_regexes(command_names)
        self.master_regex = re.compile('master|slack')
        self.channel_regex = re.compile('<\#(C[A-Z0-9]{8})>')
        self.user_regex = re.compile('<\@(U[A-Z0-9]{8})>')
        self.external_text_regexes = self.compile_external_text_regexes(
            external_texts)

    def compile_command_regexes(self, command_names):
        command_regexes = [re.compile('({0})'.format(command))
                           for command in command_names]
        return command_regexes

    def compile_external_text_regexes(self, external_texts):
        external_text_regexes = [re.compile('\\$({0})'.format(external_text))
                                 for external_text in external_texts]
        return external_text_regexes

    def find_commands(self, message_text):
        """Finds all commands in message_text.

        :param message_text: the message to search.
        :returns command_list: all commands that were found.
        """

        self.logger.debug('Finding commands...')

        commands = [self.find_command(command_regex, message_text)
                    for command_regex in self.command_regexes]

        command_list = [command for command in commands if command is not None]

        self.logger.debug('Found commands: {0}'.format(command_list))

        return command_list

    def find_command(self, command_regex, message_text):
        """Finds a specific command in message_text.

        :param command_regex: the regex for the command.
        :param message_text: the message to search.
        :returns command_match: the matching command.
        """

        self.logger.debug(
            'Finding command with regex: {0}'.format(command_regex))

        command_matches = command_regex.findall(message_text)

        if command_matches:
            command_match = command_matches[0]
            self.logger.debug('Found command: {0}'.format(command_match))
        else:
            command_match = None
            self.logger.debug('Did not find command.')

        return command_match

    def find_master(self, message_text):
        """Finds all master mentions.

        :param message_text: the message to search.
        :returns masters: a list of master mentions.
        """

        self.logger.debug('Finding master mentions.')

        masters = self.master_regex.findall(message_text)

        self.logger.debug('Found master mentions: {0}'.format(masters))

        return masters

    def find_channels(self, message_text):
        """Finds all channel mentions.

        :param message_text: the message to search.
        :returns channels: a list of channel mentions.
        """

        self.logger.debug('Finding channel mentions.')

        channels = self.channel_regex.findall(message_text)

        self.logger.debug('Found channel mentions: {0}'.format(channels))

        return channels

    def find_users(self, message_text):
        """Finds all user mentions.

        :param message_text: the message to search.
        :returns users: a list of user mentions.
        """

        self.logger.debug('Finding user mentions.')

        users = self.user_regex.findall(message_text)

        self.logger.debug('Found user mentions: {0}'.format(users))

        return users

    def find_external_texts(self, message_text):
        """Find all external text mentions.

        :param message_text: the message to search.
        :returns external_texts: a list of external text mentions.
        """

        self.logger.debug('Finding external text mentions.')

        external_texts = []
        spaceless_message = message_text.replace(' ', '')

        matches = [regex.findall(spaceless_message)
                   for regex in self.external_text_regexes]

        external_texts = list(chain.from_iterable(matches))

        self.logger.debug(
            'Found external text mentions: {0}'.format(external_texts))

        return external_texts

    def is_respondable(self, message):
        """Determines if the bot should reply to the message

        :param message: A message to qualify for a response.
        :returns respondable: True or False
        """

        if 'type' not in message:
            return False

        if 'text' not in message:
            return False

        if message['type'] != 'message':
            return False

        # Prevents loops from multiple instances.
        if 'user' in message and message['user'] == self.user_id:
            return False

        # Did the message mention the bot?
        if '<@{0}>'.format(self.user_id) in message['text']:
            return True

        if self.username.lower() in message['text'].lower():
            return True

        # Direct message
        if message['channel'].startswith("D"):
            return True

        return False
