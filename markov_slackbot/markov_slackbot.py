# -*- coding: utf-8 -*-

import time
import markovify
import re
import json

from markov_slackbot.data_clean import add_punctuation
from os import path

from os import listdir
from os.path import isfile, join

from slackclient import SlackClient


class MarkovSlackbot(object):
    """The Markov slackbot itself.
    """

    def __init__(self, config):
        """Initialize the Markov slackbot.
        """

        # Unpack Config
        self.token = config.get('SLACK_TOKEN')
        self.raw_chatlog_dir = config.get('raw_chatlog_dir')
        self.clean_chatlog_dir = config.get('clean_chatlog_dir')
        self.mixin_dir = config.get('mixin_dir')

        self.slack_client = None
        self.last_ping = 0

    def connect(self):
        """Create a client and connect to slack using the supplied token.
        """

        self.slack_client = SlackClient(self.token)
        self.slack_client.rtm_connect()

    def start(self):
        """Start the bot.
        """

        self.connect()
        self.user_id = self.slack_client.server.users.find(
            self.slack_client.server.username).id
        while True:
            for reply in self.slack_client.rtm_read():
                #print(reply)
                if (self.qualify_respondable(reply)):
                    try:
                        self.output(reply['channel'],
                                self.generate_model(reply).make_sentence())
                    except Exception as e:
                        print(e)
                        self.output(reply['channel'],
                                "I'm sorry <@" + reply['user'] + ">, I'm afraid I can't do that.")
                else:
                    if 'channel' in reply and 'text' in reply and reply['user'] != self.user_id:
                        p = path.join(self.clean_chatlog_dir, self.slack_client.server.channels.find(reply['channel']).name, 'learning.txt')
                        with open(p, 'a') as f:
                            f.write(add_punctuation([reply['text']]) + '\n')
            self.autoping()
            time.sleep(.1)

    def autoping(self):
        """Ping slack every three seconds.
        """

        now = int(time.time())
        if now > self.last_ping + 3:
            self.slack_client.server.ping()
            self.last_ping = now

    def output(self, channel, message):
        """Output message to channel.

        :param channel: A slack channel.
        :param message: The message to send.
        """

        channel = self.slack_client.server.channels.find(channel)
        channel.send_message(message)

    def qualify_respondable(self, reply):
        """Determines if the bot should reply to the message

        :param reply: A message to qualify for a response.
        """

        if 'type' not in reply:
            return False

        if 'text' not in reply:
            return False

        if reply['type'] != 'message':
            return False

        # Prevents loops from multiple instances.
        if 'user' in reply and reply['user'] == self.user_id:
            return False

        # Did the message mention the bot?
        if ('<@' + self.user_id + '>' in reply['text'] or
           self.slack_client.server.username.lower() in reply['text'].lower() or
           reply['channel'].startswith("D")):
            return True
        else:
            return False

    def generate_model(self, reply):
        # Get raw text as string.
        channels = ['general', 'random', 'batsignal', 'node', 'whitby']
        paths = []
        for c in channels:
            paths.append(path.join(self.clean_chatlog_dir, c))

        text = ''
        for p in paths:
            onlyfiles = [f for f in listdir(p) if isfile(join(p, f))]

            for file in onlyfiles:
                with open(join(p, file)) as f:
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

        #check if we have mixins
        search = re.search('(' + '|'.join(dictionary['small'] + dictionary['big']) + ')', reply['text'])
        if search:
            params = reply['text'][search.start():].split(' and')

        for param in params:
            if re.search('(' + '|'.join(dictionary['small']) + ')', param):
                mixin_weights.append(0.5)
            elif re.search('(' + '|'.join(dictionary['big']) + ')', param):
                mixin_weights.append(2)

            model_param = re.sub('(' + '|'.join(dictionary['small'] + dictionary['big']) + ')', '', param)
            model_param = re.sub(' ', '', model_param).lower()

            with open(path.join(self.mixin_dir, model_param,
                      model_param + '.txt')) as f:
                text = f.read()
            mixin_models.append(markovify.Text(text))

        mixin_models.append(text_model)
        mixin_weights.append(0.1)

        return markovify.combine(mixin_models, mixin_weights)
