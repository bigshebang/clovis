#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'alabaster>=0.7.8',
    'argh>=0.26.2',
    'Babel>=2.3.4',
    'cffi>=1.7.0',
    'click>=6.6',
    'cryptography>=1.4',
    'idna>=2.1',
    'imagesize>=0.7.1',
    'Jinja2>=2.8',
    'MarkupSafe>=0.23',
    'mccabe>=0.5.0',
    'pathtools>=0.1.2',
    'pluggy>=0.3.1',
    'py>=1.4.31',
    'pyasn1>=0.1.9',
    'pycodestyle>=2.0.0',
    'pycparser>=2.14',
    'pyflakes>=1.2.3',
    'Pygments>=2.1.3',
    'pytest>=2.9.2',
    'pytz>=2016.6.1',
    'PyYAML>=3.11',
    'requests>=2.10.0',
    'six>=1.10.0',
    'slackclient>=1.0.1',
    'snowballstemmer>=1.2.1',
    'watchdog>=0.8.3',
    'websocket-client>=0.37.0',
    'pandas>=0.18.1'
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='markov_slackbot',
    version='0.1.0',
    description="Markov Slackbot is a Slack chatbot that uses Markov chains.",
    long_description=readme + '\n\n' + history,
    author="Stuart Squires",
    author_email='StuartJSquires@gmail.com',
    url='https://github.com/StuartJSquires/markov_slackbot',
    packages=[
        'markov_slackbot',
    ],
    package_dir={'markov_slackbot':
                 'markov_slackbot'},
    entry_points={
        'console_scripts': [
            'markov_slackbot=markov_slackbot.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='markov_slackbot',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
