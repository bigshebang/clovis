# -*- coding: utf-8 -*-

import time

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
        self.user_id = self.slack_client.server.users.find(self.slack_client.server.username).id
        while True:
            for reply in self.slack_client.rtm_read():
                print(reply)
                if ('type' in reply and
                    reply['type'] == 'message' and 
                    ('<@' + self.user_id + '>' in reply['text'] or 
                        self.slack_client.server.username in reply['text']
                    )):
                    self.output('#markov-sandbox', reply['text'])
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
