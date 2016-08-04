# -*- coding: utf-8 -*-

import logging
from os import listdir
from os import path
import re
import time

import markovify
from slackclient import SlackClient

import markov_slackbot.data_clean as data_clean


class MarkovSlackbot(object):
    """The Markov slackbot itself.
    """

    def __init__(self, config):
        """Initialize the Markov slackbot.
        """

        self.logger = logging.getLogger(__name__)
        self.last_ping = 0

        # Unpack Config
        self.token = config.get('SLACK_TOKEN')
        self.raw_chatlog_dir = config.get('raw_chatlog_dir')
        self.clean_chatlog_dir = config.get('clean_chatlog_dir')
        self.mixin_dir = config.get('mixin_dir')
        self.send_mentions = config.get('mentions')

        self.slack_client = SlackClient(self.token)

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

        while True:
            messages = self.slack_client.rtm_read()

            for message in messages:
                if (self.qualify_respondable(message)):
                    self.respond(message)
                elif (self.qualify_learnable(message)):
                    self.learn_from_message(message)

            self.autoping()
            time.sleep(.1)

    def set_user_info(self):
        """Sets the bot's user info so that it can reply to mentions.
        """
        self.username = self.slack_client.server.username
        user = self.slack_client.server.users.find(self.username)
        self.user_id = user.id

    def qualify_respondable(self, message):
        """Determines if the bot should reply to the message

        :param message: A message to qualify for a response.
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

    def respond(self, message):
        """Respond to message.
        """
        try:
            response = self.generate_model(message).make_sentence()
            self.send_message(message['channel'], response)
        except Exception:
            self.logger.exception('Slack command parsing error.')
            self.send_message(
                message['channel'],
                ("I'm sorry <@{0}>, I'm afraid I can't do" +
                 " that.")).format(message['user'])

    def qualify_learnable(self, message):
        """Determine if the message should be used for learning.
        """
        return ('channel' in message and 'text' in message and
                'user' in message and message['user'] != self.user_id)

    def learn_from_message(self, message):
        p = path.join(
            self.clean_chatlog_dir,
            self.slack_client.server.channels.find(
                message['channel']).name, 'learning.txt')

        with open(p, 'a') as f:
            f.write(data_clean.add_punctuation([message['text']]) + '\n')

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

    def generate_model(self, reply):
        # Get raw text as string.
        channels = ['general', 'random', 'batsignal', 'node', 'whitby']
        paths = []
        for c in channels:
            paths.append(path.join(self.clean_chatlog_dir, c))

        text = ''
        for p in paths:
            onlyfiles = [f for f in listdir(p) if path.isfile(path.join(p, f))]

            for file in onlyfiles:
                with open(path.join(p, file)) as f:
                    text += f.read()

        # Build the model.
        text_model = markovify.Text(text)

        mixin_models = []
        mixin_weights = []
        params = []

        dictionary = {
            'small': [
                'a little of',
                'a little',
                'some of',
                'a little bit of',
                'a bit of',
                'a dash of',
                'just a dash of',
                'less'
            ],
            'big': [
                'a lot of',
                'a ton of',
                'a whole bunch of',
                'a large amount of',
                'a shitload of',
                'a shitstorm of',
                'lots of',
                'more'
            ]
        }

        # check if we have mixins
        search = re.search(
            '({0})'.format('|'.join(dictionary['small'] + dictionary['big'])),
            reply['text'])

        if search:
            params = reply['text'][search.start():].split(' and')

        for param in params:
            if re.search('({0})'.format('|'.join(dictionary['small'])), param):
                mixin_weights.append(0.5)
            elif re.search('({0})'.format('|'.join(dictionary['big'])), param):
                mixin_weights.append(2)

            model_param = re.sub(
                '({0})'.format(
                    '|'.join(dictionary['small'] + dictionary['big'])),
                '',
                param)

            model_param = re.sub(' ', '', model_param).lower()

            with open(
                path.join(
                    self.mixin_dir,
                    model_param,
                    model_param + '.txt')) as f:
                text = f.read()

            mixin_models.append(markovify.Text(text))

        mixin_models.append(text_model)
        mixin_weights.append(0.1)

        return markovify.combine(mixin_models, mixin_weights)

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
