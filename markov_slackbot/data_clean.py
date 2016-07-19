import pandas as pd
from os import path, listdir


class Data(object):
    def __init__(self):
        messages_dir = path.join(path.pardir, 'data', 'messages')
        self.messages_file = open(path.join(messages_dir, 'messages.txt'), 'a')
        self.messages_file.seek(0)
        self.messages_file.truncate()

    def clean_data(self, data):
        """Removes all messages that contain subtypes (ie. not clean messages
        (comments, file uploads).
        :param data: A file containing Slack logs.
        """
        # regex will clean all reaction from messages
        messages = data[(data['type'] == 'message') &
                        ('subtype' not in data.columns)]

        # replace in line sections (ie ``` code ```)
        messages['text'] = messages['text'].str.replace(r'(```)[^;]*(```)', '')
        # replace reaction in text
        messages['text'] = messages['text'].str.replace(r'(:)[^<>]*(:)', '')
        # replace every <> except for mentions
        messages['text'] = messages['text'].str.replace(r'(<)[^!@<>]*(>)', '')
        # replace &gt;
        messages['text'] = messages['text'].str.replace('&gt;', '')
        # replace ": "
        messages['text'] = messages['text'].str.replace(': ', '')
        # replace " \\' " with " ' "
        messages['text'] = messages['text'].str.replace("\\'", "'")
        # replace &amp;
        # messages['text'] = messages['text'].str.replace('&amp;', '')
        # encode to string
        return messages['text'].astype(str)

    def write_to_file(self, messages):
        """Open file and append messages to text.

        :param messages: Messages to append.
        """

        messages_file = open(path.join(path.pardir, 'data', 'messages',
                             'messages.txt'), 'a')

        for message in messages:
            if(len(message.strip(' ')) > 0):
                last_char = message.strip(' ')[-1][-1]
                if (not last_char == '.' and
                    not last_char == '?' and
                    not last_char == '!' and
                    not last_char == '\n' and
                   len("".join(message.split(' '))) > 0 and
                   len(message) > 0):
                    message += '. '
                messages_file.write(message)
        messages_file.close

    def get_data(self):
        folders = listdir(path.join(path.pardir, 'data'))
        print(folders)
        for folder in folders:
            if folder == 'messages':
                continue
            files = listdir(path.join(path.pardir, 'data', folder))
            for file in files:
                if('json' in file):
                    file = pd.read_json(path.join(path.pardir, 'data', folder,
                                        file))
                    messages = self.clean_data(file)
                    self.write_to_file(messages)


def main():
    data = Data()
    data.get_data()


def parse_slack_json(raw_file_json):
    """Clean raw Slack logs.

    :param raw_file_json: The json to clean.
    :returns: The cleaned data.
    """

    stripped_data = remove_subtypes(raw_file_json)
    clean_data = add_punctuation(stripped_data)
    return clean_data


def remove_subtypes(data):
    """Removes all messages that contain subtypes (ie. not clean messages
    (comments, file uploads).
    :param data: A file containing Slack logs.
    """

    # regex will clean all reaction from messages
    messages = data[(data['type'] == 'message') &
                    ('subtype' not in data.columns)]

    # replace in line sections (ie ``` code ```)
    messages['text'] = messages['text'].str.replace(r'(```)[^;]*(```)', '')
    # replace reaction in text
    messages['text'] = messages['text'].str.replace(r'(:)[^<>]*(:)', '')
    # replace every <>
    messages['text'] = messages['text'].str.replace(r'(<)[^<>]*(>)', '')
    # replace &gt;
    messages['text'] = messages['text'].str.replace('&gt;', '')
    # replace &amp;
    messages['text'] = messages['text'].str.replace('&amp;', '')
    # encode to string
    return messages['text'].astype(str)


def add_punctuation(stripped_data):
    """Add periods to messages with no punctuation.

    :param stripped_data: Already stripped down Slack data.
    :returns punctuated_data: Data with punctuation.
    """

    punctuated_data = ''

    for message in stripped_data:
        if ((not message.endswith('.') or
            not message.endswith('?') or
           not message.endswith('!')) and
           len(message) > 0):
            message += '. '
        punctuated_data += message

    return punctuated_data


if __name__ == "__main__":
    main()
