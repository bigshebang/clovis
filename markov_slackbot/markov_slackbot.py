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
        while True:
            self.autoping()
            time.sleep(.1)

    def autoping(self):
        now = int(time.time())
        if now > self.last_ping + 3:
            self.slack_client.server.ping()
            self.last_ping = now
