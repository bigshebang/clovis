# -*- coding: utf-8 -*-

import time
import markovify
import re
from os import path

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
                    # Get raw text as string.
                    with open(path.join(path.pardir, 'data', 'messages',
                                        'messages.txt')) as f:
                        text = f.read()

                    # Build the model.
                    text_model = markovify.Text(text)

                    mixins = []

                    params = re.sub('(<@' + self.user_id + '>|marky)', '',
                                    reply['text']).split()

                    for param in params:
                        with open(path.join(path.pardir, 'data', param,
                                  param + '.txt')) as f:
                            text = f.read()
                        mixins.append(markovify.Text(text))

                    mixins.append(text_model)
                    combined_model = markovify.combine(mixins, [1.8, .2])

                    self.output(reply['channel'],
                                combined_model.make_sentence())
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
        if reply['user'] == self.user_id:
            return False

        # Did the message mention the bot?
        if ('<@' + self.user_id + '>' in reply['text'] or
           self.slack_client.server.username in reply['text'] or
           reply['channel'].startswith("D")):
            return True
        else:
            return False
