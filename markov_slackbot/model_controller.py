# -*- coding: utf-8 -*-

import logging
import re

import markovify


class ModelController(object):
    """
    """

    def __init__(self, user_id, slack_logs, external_texts):
        self.logger = logging.getLogger(__name__)
        self.user_id = user_id

        self.replacement_functions = self.build_replacement_functions()

        self.master_model = self.generate_slack_model(slack_logs.master_log)

        self.channel_models = self.generate_slack_models(
            slack_logs.channel_logs)
        self.user_models = self.generate_slack_models(slack_logs.user_logs)
        self.external_models = self.generate_external_models(external_texts)

    def build_replacement_functions(self):
        regex_replacement_pairs = (
            (re.compile('```(?:[^`]+|`(?!``))*```', flags=re.M), ''),
            (re.compile('(<)[^!@<>]*(>)'), ''))

        replacement_functions = [lambda m: regex.sub(replacement, m)
                                 for regex, replacement
                                 in regex_replacement_pairs]

        return replacement_functions

    def generate_slack_models(self, logs):
        models = {key: self.generate_slack_model(log)
                  for key, log in logs.items()}
        return models

    def generate_slack_model(self, log):
        """Generates a markovify text model from log.

        :param log: the log to use for training.
        :returns model: a markovify Text model.
        """

        cleaned_messages = [self.parse_message(message)
                            for message in log]

        cleaned_messages = [message
                            for message in cleaned_messages
                            if message is not None]

        training_text = '\n'.join(cleaned_messages)

        model = markovify.Text(training_text)

        return model

    def parse_message(self, message):
        """
        """

        if not self.is_learnable(message):
            return None

        cleaned_message = message['text']

        for replacement_function in self.replacement_functions:
            cleaned_message = replacement_function(cleaned_message)

        return cleaned_message

    def is_learnable(self, message):
        if 'subtype' in message:
            return False

        if 'text' not in message:
            return False

        if 'user' not in message:
            return False

        if message['user'] == self.user_id:
            return False

        return True

    def generate_external_models(self, external_texts):
        external_models = {name: markovify.Text(text)
                           for name, text in external_texts.items()}
        return external_models

    def build_message(self, masters, channel_names, users, external_texts):
        models = []

        for master in masters:
            models += [self.master_model]

        for channel_name in channel_names:
            channel_model = self.channel_models.get(channel_name)
            if channel_model is not None:
                models += [channel_model]

        for user in users:
            user_model = self.user_models.get(user)
            if user_model is not None:
                models += [user_model]

        for external_text in external_texts:
            external_model = self.external_models.get(external_text)
            if external_model is not None:
                models += [external_model]

        if models:
            message = markovify.combine(models).make_sentence()
        else:
            message = self.master_model.make_sentence()

        return message

    def regenerate_slack_models(self, slack_logs, channel_name, user):
        self.master_model = self.generate_slack_model(slack_logs.master)
        self.channel_models = self.generate_models(
            slack_logs.channels[channel_name])
        self.user_models = self.generate_models(
            slack_logs.users[user])
