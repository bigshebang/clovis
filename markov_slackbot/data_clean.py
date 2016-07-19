# -*- coding: utf-8 -*-


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
    # replace every <> except for mentions
    messages['text'] = messages['text'].str.replace(r'(<)[^!@<>]*(>)', '')
    # replace &gt;
    messages['text'] = messages['text'].str.replace('&gt;', '')
    # replace " \\' " with " ' "
    messages['text'] = messages['text'].str.replace("\\'", "'")

    # encode to string
    return messages['text'].astype(str)


def add_punctuation(stripped_data):
    """Add periods to messages with no punctuation.

    :param stripped_data: Already stripped down Slack data.
    :returns punctuated_data: Data with punctuation.
    """

    punctuated_data = ''

    for message in stripped_data:
        if(len(message.strip(' ')) > 0):
            last_char = message.strip(' ')[-1][-1]
            if (not last_char == '.' and
                not last_char == '?' and
                not last_char == '!' and
                not last_char == '\n' and
               len("".join(message.split(' '))) > 0 and
               len(message) > 0):
                message += '.'
            punctuated_data += message + ' '

    return punctuated_data
