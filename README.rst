===============================
Markov Slackbot
===============================


.. image:: https://img.shields.io/pypi/v/markov_slackbot.svg
        :target: https://pypi.python.org/pypi/markov_slackbot

.. image:: https://img.shields.io/travis/StuartJSquires/markov_slackbot.svg
        :target: https://travis-ci.org/StuartJSquires/markov_slackbot

.. image:: https://readthedocs.org/projects/markov-slackbot/badge/?version=latest
        :target: https://markov-slackbot.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/StuartJSquires/markov_slackbot/shield.svg
     :target: https://pyup.io/repos/github/StuartJSquires/markov_slackbot/
     :alt: Updates


Markov Slackbot is a Slack chatbot that uses Markov chains.


* Free software: MIT license
* Documentation: https://markov-slackbot.readthedocs.io.


Features
--------

This slackbot can use multiple different models to output unique messages in channels that the bot belongs to.
In order to speak with the markov bot, invite the bot to the channel.

Once the bot is in the channel, you can interact with the bot by calling it's name, or by mentioning the bot.
To mix different models in the response, indicate the level interaction each model should have in the response
```
hey marky, give me a lot of lahey
```
```
hey marky, give me a lot of lahey and a little star wars
```

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
