# -*- coding: utf-8 -*-

import time
import markovify
import re
import json
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
                if (self.qualify_respondable(reply)):
                    try:
                        self.output(reply['channel'],
                                self.generate_model(reply).make_sentence())
                    except Exception as e:
                        print(e)
                        self.output(reply['channel'],
                                "I'm sorry <@" + reply['user'] + ">, I'm afraid I can't do that.")
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

        if reply['type'] != 'message':
            return False

        # Prevents loops from multiple instances.
        if 'user' in reply and reply['user'] == self.user_id:
            return False

        # Did the message mention the bot?
        if ('<@' + self.user_id + '>' in reply['text'] or
           self.slack_client.server.username in reply['text'] or
           reply['channel'].startswith("D")):
            return True
        else:
            return False

    def generate_model(self, reply):
        # Get raw text as string.
        channels = ['general', 'random']
        paths = []
        for c in channels:
            paths.append(path.join(path.pardir, 'cleandata', c))

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

        dictionary = json.loads(open('dictionary.json').read())

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

            with open(path.join(path.pardir, 'mixins', model_param,
                      model_param + '.txt')) as f:
                text = f.read()
            mixin_models.append(markovify.Text(text))

        mixin_models.append(text_model)
        mixin_weights.append(0.5)

        return markovify.combine(mixin_models, mixin_weights)
