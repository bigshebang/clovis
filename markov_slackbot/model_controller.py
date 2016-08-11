# -*- coding: utf-8 -*-

import logging
import re

import markovify


class ModelController(object):
    """
    """

    def __init__(self, user_id, username, slack_logs, external_texts):
        self.logger = logging.getLogger(__name__)
        self.logger.info('Initializing model controller.')

        self.user_id = user_id
        self.username = username

        self.replacement_functions = self.build_replacement_functions()

        self.master_model = self.generate_slack_model(slack_logs.master_log)

        self.logger.info(
            'Generating {0} channel models'.format(
                len(slack_logs.channel_logs)))

        self.channel_models = self.generate_slack_models(
            slack_logs.channel_logs)

        self.logger.info(
            'Generating {0} user models'.format(len(slack_logs.user_logs)))

        self.user_models = self.generate_slack_models(slack_logs.user_logs)

        self.logger.info(
            'Generating {0} external models'.format(len(external_texts)))

        self.external_models = self.generate_external_models(external_texts)

    def build_replacement_functions(self):
        """Compile regexes and create sub functions with them.

        :returns replacement_functions: a list of replacement functions.
        """

        self.logger.debug('Compiling regexes.')

        regex_replacement_pairs = (
            (re.compile('```(?:[^`]+|`(?!``))*```', flags=re.M), ''),
            (re.compile('(<)[^!@<>]*(>)'), ''))

        self.logger.debug('Building regex sub functions.')

        replacement_functions = [lambda m: regex.sub(replacement, m)
                                 for regex, replacement
                                 in regex_replacement_pairs]

        return replacement_functions

    def generate_slack_models(self, logs):
        """Generate slack Markovify models.

        :param logs: a dict of logs with their names.
        :returns models: a dict of models with their names.
        """

        self.logger.debug(
            'Generating slack models for logs with length: {0}'.format(
                len(logs)))

        potential_models = {key: self.generate_slack_model(log)
                            for key, log in logs.items()}

        models = {key: model
                  for key, model in potential_models.items()
                  if model is not None}

        self.logger.debug('Generated slack models: {0}'.format(models))

        return models

    def generate_slack_model(self, log):
        """Generates a markovify text model from log.

        :param log: the log to use for training.
        :returns model: a markovify Text model.
        """

        self.logger.debug(
            'Generating slack model for log with length: {0}'.format(len(log)))

        cleaned_messages = [self.parse_message(message)
                            for message in log]

        non_empty_cleaned_messages = [message
                                      for message in cleaned_messages
                                      if message is not None]

        punctuated_messages = []

        for message in non_empty_cleaned_messages:
            if not re.findall('(\.|\?|\!)$', message):
                punctuated_messages = [message + '.']
            else:
                punctuated_messages += [message]

        if non_empty_cleaned_messages:
            training_text = '.\n'.join(non_empty_cleaned_messages)

            model = markovify.Text(training_text)

            self.logger.debug('Generated slack model: {0}'.format(model))

        else:
            self.logger.debug('Did not generate slack model.')
            model = None

        return model

    def parse_message(self, message):
        """Parses and cleans a message.

        :param message: a message object.
        :return cleaned_message: cleaned message text.
        """

        # self.logger.debug('Parsing message: {0}'.format(message))

        if not self.is_learnable(message):
            return None

        cleaned_message = message['text']

        # self.logger.debug(
        #     'Cleaning message text: {0}'.format(cleaned_message))

        for replacement_function in self.replacement_functions:
            cleaned_message = replacement_function(cleaned_message)

        # self.logger.debug('Cleaned message text: {0}'.format(cleaned_message))

        return cleaned_message

    def is_learnable(self, message):
        """Determines if a message is learnable.

        :param message: the message to validate.
        :returns learnable: whether or not the message is learnable.
        """

        if 'text' not in message:
            return False

        if 'subtype' in message:
            return False

        if 'user' not in message:
            return False

        if message['user'] == self.user_id:
            return False

        if self.user_id in message['text']:
            return False

        if self.username in message['text']:
            return False

        if 'channel' in message:
            if message['channel'][0] is 'D':
                return False

        return True

    def generate_external_models(self, external_texts):
        external_models = {name: markovify.Text(text)
                           for name, text in external_texts.items()}
        return external_models

    def build_message(self, masters, channel_names, users, external_texts):
        self.logger.debug('Building response.')

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
            self.logger.debug('Using models: {0}'.format(models))
            for i in range(20):
                message = markovify.combine(models[:5]).make_sentence()
                self.logger.debug('Tried to build message...')
                if message:
                    break
        else:
            self.logger.debug('No models, using master.')
            message = self.master_model.make_sentence()

        self.logger.debug(
            'Built response: {0}'.format(message))

        if message is None:
            self.logger.debug('Could not build message from model.')
            message = ('I\'m sorry, I couldn\'t build a message using that ' +
                       'model.')

        return message

    def regenerate_slack_models(self, slack_logs, channel_name, user):
        self.master_model = self.generate_slack_model(slack_logs.master_log)
        self.channel_models[channel_name] = self.generate_slack_model(
            slack_logs.channel_logs[channel_name])
        self.user_models[user] = self.generate_slack_model(
            slack_logs.user_logs[user])
