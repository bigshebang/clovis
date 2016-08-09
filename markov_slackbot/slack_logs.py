# -*- coding: utf-8 -*-

from itertools import chain
import datetime
import json
import logging
import os


class SlackLogs(object):
    def __init__(self, slack_log_dir):
        self.logger = logging.getLogger(__name__)
        self.slack_log_dir = slack_log_dir

        self.prepare_slack_log_dir()

        self.channel_logs = self.read_log_directory()

        self.master_log = list(chain.from_iterable(self.channel_logs.values()))
        self.user_logs = self.split_log_by_user(self.master_log)

    def prepare_slack_log_dir(self):
        if not os.path.exists(self.slack_log_dir):
            os.makedirs(self.slack_log_dir)

    def read_log_directory(self):
        """Reads a directory of slack log folders, returns a dictionary
        containing the logs as objects with the channels as the keys.

        :param slack_log_dir: directory containing slack log folders.
        :returns logs: dictionary containing slack log data by channel.
        """
        self.logger.info('Starting log reading.')

        channel_dirs = os.listdir(self.slack_log_dir)
        channel_paths = [os.path.join(self.slack_log_dir, channel_dir)
                         for channel_dir in channel_dirs]

        logs = {channel_folder: self.read_channel_logfiles(channel_path)
                for channel_folder, channel_path
                in zip(channel_dirs, channel_paths)}

        return logs

    def read_channel_logfiles(self, channel_folder):
        channel_log = [self.read_logfile(os.path.join(
                        channel_folder, log_filename))
                       for log_filename
                       in os.listdir(channel_folder)]

        return list(chain.from_iterable(channel_log))

    def read_logfile(self, log_filename):
        log_file = open(log_filename, 'r')
        channel_log = json.load(log_file)
        log_file.close()

        return channel_log

    def split_log_by_user(self, log):
        """Splits log into a dict of logs separated by user.

        :param log: the log to split.
        :returns user_logs: a dict of logs with users as keys.
        """

        user_logs = {}

        for message in log:
            if 'user' in message:
                if message['user'] in user_logs:
                    user_logs['user'] += [message]
                else:
                    user_logs['user'] = [message]

        return user_logs

    def add_to_logs(self, message, channel_name):
        """Adds a message to logs in memory and saves to log directory.
        """

        if channel_name is None:
            return

        self.master_log += message

        user = message.get('user')

        if user in self.user_logs:
            self.user_logs[user] += [message]
        else:
            self.user_logs[user] = [message]

        if channel_name in self.channel_logs:
            self.channel_logs[channel_name] += [message]
        else:
            self.channel_logs[channel_name] = [message]

        self.write_to_logfile(message, channel_name)

    def write_to_logfile(self, message, channel_name):
        today = datetime.date.today()

        today_string = today.isoformat()

        filename = '{0}.json'.format(today_string)

        channel_dir = os.path.join(self.slack_log_dir, channel_name)

        if not os.path.exists(channel_dir):
            os.makedirs(channel_dir)

        file_path = os.path.join(channel_dir, filename)

        if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, 'r') as log_file:
                existing_log = json.loads(log_file.read())
            log = existing_log + [message]
        else:
            log = [message]

        log_json = json.dumps(log, indent=4)

        with open(file_path, 'w+') as log_file:
            log_file.write(log_json)
