#!/usr/bin/env python2

from setuptools import setup, find_packages

requires = open('requirements.txt').read().split('\n')

setup(
    name='hamper',
    version='1.9.1',
    description='Yet another IRC bot',
    install_requires=requires,
    author='Mike Cooper',
    author_email='mythmon@gmail.com',
    url='https://www.github.com/hamperbot/hamper',
    packages=find_packages(),
    entry_points = {
        'console_scripts': [
            'hamper = hamper.commander:main',
        ],
        'hamperbot.plugins': [
                'karma = hamper.plugins.karma:Karma',
                'friendly = hamper.plugins.friendly:Friendly',
                'bitly = hamper.plugins.bitly:Bitly',
                'channel_utils = hamper.plugins.channel_utils:ChannelUtils',
                'lmgtfy = hamper.plugins.commands:LetMeGoogleThatForYou',
                'rot13 = hamper.plugins.commands:Rot13',
                'quit = hamper.plugins.commands:Quit',
                'dice = hamper.plugins.commands:Dice',
                'sed = hamper.plugins.commands:Sed',
                'lookup = hamper.plugins.dictionary:Lookup',
                'factoids = hamper.plugins.factoids:Factoids',
                'flip = hamper.plugins.flip:Flip',
                'botsnack = hamper.plugins.friendly:BotSnack',
                'ponies = hamper.plugins.friendly:OmgPonies',
                'goodbye = hamper.plugins.goodbye:GoodBye',
                'help = hamper.plugins.help:Help',
                'yesno = hamper.plugins.questions:YesNoPlugin',
                'choices = hamper.plugins.questions:ChoicesPlugin',
                'quotes = hamper.plugins.quotes:Quotes',
                'remindme = hamper.plugins.remindme:Reminder',
                'roulette = hamper.plugins.roulette:Roulette',
                'seen = hamper.plugins.seen:Seen',
                'suggest = hamper.plugins.suggest:Suggest',
                'timez = hamper.plugins.timez:Timez',
                'tinyurl = hamper.plugins.tinyurl:Tinyurl',
                'whatwasthat = hamper.plugins.whatwasthat:WhatWasThat',
            ],
    },
)
