# -*- coding: utf-8 -*-

import time
import markovify
from os import path

from slackclient import SlackClient


class MarkovSlackbot(object):
    """
    """

    def __init__(self, config):
        """
        """

        self.token = config.get('SLACK_TOKEN')
        print(self.token)

        self.slack_client = None
        self.last_ping = 0

    def connect(self):
        """
        """

        self.slack_client = SlackClient(self.token)
        self.slack_client.rtm_connect()

    def start(self):
        self.connect()
        self.user_id = self.slack_client.server.users.find(
            self.slack_client.server.username).id
        while True:
            for reply in self.slack_client.rtm_read():
                print(reply)
                if (self.qualify_respondable(reply)):
                    # Get raw text as string.
                    with open(path.join(path.pardir, 'data', 'messages',
                                        'messages.txt')) as f:
                        text = f.read()

                    # Build the model.
                    text_model = markovify.Text(text)

                    self.output('#markov-sandbox', text_model.make_sentence())
            self.autoping()
            time.sleep(.1)

    def autoping(self):
        now = int(time.time())
        if now > self.last_ping + 3:
            self.slack_client.server.ping()
            self.last_ping = now

    def output(self, channel, message):
        channel = self.slack_client.server.channels.find(channel)
        channel.send_message(message)

    def qualify_respondable(self, reply):
        """
        """
        if 'type' not in reply:
            return False

        if reply['type'] != 'message':
            return False

        if reply['user'] == self.user_id:
            return False

        if ('<@' + self.user_id + '>' in reply['text'] or
           self.slack_client.server.username in reply['text']):
            return True
        else:
            return False
