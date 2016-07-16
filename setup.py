#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    # TODO: put package requirements here
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
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
