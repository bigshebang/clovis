# -*- coding: utf-8 -*-

import logging
import os
from os import path
import re
import time

from slackclient import SlackClient

import markov_slackbot.model_controller as model_controller
import markov_slackbot.message_interpreter as message_interpreter
import markov_slackbot.slack_logs as slack_logs


class MarkovSlackbot(object):
    """The Markov slackbot itself.
    """

    def __init__(self, config):
        """Initialize the Markov slackbot.
        """

        self.logger = logging.getLogger(__name__)
        self.last_ping = 0
        self.commands = {
            "help": lambda channel: self.send_help_message(channel)
        }

        # Unpack Config
        self.token = config.get('SLACK_TOKEN')
        self.slack_log_dir = config.get('slack_log_dir')
        self.send_mentions = config.get('mentions')

        external_texts_dir = config.get('external_texts_dir')
        self.external_texts = self.load_external_texts(external_texts_dir)

        self.slack_logs = slack_logs.SlackLogs(self.slack_log_dir)

        self.slack_client = SlackClient(self.token)

    def load_external_texts(self, external_texts_dir):
        self.logger.info('Loading external texts.')
        external_texts = {}
        for external_text_filename in os.listdir(external_texts_dir):
            external_text_filepath = os.path.join(
                external_texts_dir,
                external_text_filename)
            with open(external_text_filepath, 'r') as external_text_file:
                text_name = path.splitext(external_text_filename)[0]
                external_texts[text_name] = external_text_file.read()
        return external_texts

    def start(self):
        """Start the bot.
        """
        while True:
            try:
                self.main_loop()
            except Exception:
                self.logger.exception('Fatal error in main loop.')

    def main_loop(self):
        """The main loop for the bot.
        """

        self.slack_client.rtm_connect()
        self.set_user_info()
        self.model_controller = model_controller.ModelController(
            self.user_id,
            self.slack_logs,
            self.external_texts)
        self.message_interpreter = message_interpreter.MessageInterpreter(
            self.user_id,
            self.username,
            self.commands.keys(),
            self.external_texts.keys())

        while True:
            messages = self.slack_client.rtm_read()

            for message in messages:
                channel_name = self.get_channel_name(message.get('channel'))
                self.slack_logs.add_to_logs(message, channel_name)

                if (self.message_interpreter.is_respondable(message)):
                    self.respond(message)
                elif (self.model_controller.is_learnable(message)):
                    self.regenerate_slack_models(
                        self.slack_logs,
                        channel_name,
                        message['user'])

            self.autoping()
            time.sleep(.1)

    def set_user_info(self):
        """Sets the bot's user info so that it can reply to mentions.
        """
        self.username = self.slack_client.server.username
        user = self.slack_client.server.users.find(self.username)
        self.user_id = user.id

    def respond(self, message):
        """Respond to message.
        """
        try:
            message_text = message['text']
            channel = message['channel']
            commands = self.message_interpreter.find_commands(message_text)

            if commands:
                for command_name in commands:
                    command_name = self.commands[command_name]
                    command_name(channel)
            else:
                masters = self.message_interpreter.find_master(message_text)
                channels = self.message_interpreter.find_channels(message_text)
                channel_names = [self.get_channel_name(channel)
                                 for channel in channels]
                users = self.message_interpreter.find_users(message_text)
                external_texts = self.message_interpreter.find_external_texts(
                    message_text)

                response = self.model_controller.build_message(
                    masters,
                    channel_names,
                    users,
                    external_texts)

                self.send_message(channel, response)
        except Exception:
            self.logger.exception('Slack command parsing error.')
            self.send_message(
                message['channel'],
                ("I'm sorry <@{0}>, I'm afraid I can't do" +
                 " that.").format(message['user']))

    def autoping(self):
        """Ping slack every three seconds.
        """

        now = int(time.time())
        if now > self.last_ping + 3:
            self.slack_client.server.ping()
            self.last_ping = now

    def send_message(self, channel, message):
        """Send message to channel.

        :param channel: A slack channel.
        :param message: The message to send.
        """

        if not self.send_mentions:
            message = self.clean_reply(message)

        self.slack_client.rtm_send_message(channel, message)

    def clean_reply(self, message):
        """Cleans message of mentions and bangs.
        """

        mention_pattern = '<@([0-9A-z]+)>'
        bang_pattern = '<!([0-9A-z]+)>'

        mentionless_message = re.sub(
            mention_pattern,
            self.replace_mention,
            message)

        clean_message = re.sub(
            bang_pattern,
            self.replace_bang,
            mentionless_message)

        return clean_message

    def replace_mention(self, match_obj):
        return '@' + self.get_username(match_obj.group(1))

    def replace_bang(match_obj):
        return '!' + match_obj.group(1)

    def get_username(self, user_id):
        user = self.slack_client.server.users.find(user_id)
        return user.name

    def get_channel_name(self, channel_id):
        channel = self.slack_client.server.channels.find(channel_id)
        if channel is None:
            return channel
        else:
            return channel.name

    def send_help_message(self, channel):
        message = """There are a few things I can do:

If you say `slack`, or `master`, I will speak using everything I have
learned from slack. This is my default behaviour.

If you say `#channel`, I will speak using everything I have learned
from that channel.

If you say `@user`, I will speak using everything I have learned from
that user.

If you say `$external source`, I will speak using everything I have
learned from that source.

Hint: You can combine multiple commands.
        """
        self.send_message(channel, message)
