#!/usr/bin/env python2

from setuptools import setup, find_packages

requires = open('requirements.txt').read().split('\n')

setup(
    name='hamper',
    version='1.11.1',
    description='Yet another IRC bot',
    install_requires=requires,
    author='Mike Cooper',
    author_email='mythmon@gmail.com',
    url='https://www.github.com/hamperbot/hamper',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'hamper = hamper.commander:main',
        ],
        'hamperbot.plugins': [
            'bitly = hamper.plugins.bitly:Bitly',
            'botsnack = hamper.plugins.friendly:BotSnack',
            'channel_utils = hamper.plugins.channel_utils:ChannelUtils',
            'choices = hamper.plugins.questions:ChoicesPlugin',
            'foods = hamper.plugins.questions:FoodsPlugin',
            'dice = hamper.plugins.commands:Dice',
            'factoids = hamper.plugins.factoids:Factoids',
            'flip = hamper.plugins.flip:Flip',
            'friendly = hamper.plugins.friendly:Friendly',
            'goodbye = hamper.plugins.goodbye:GoodBye',
            'help = hamper.plugins.help:Help',
            'karma = hamper.plugins.karma:Karma',
            'karma_adv = hamper.plugins.karma_adv:KarmAdv',
            'lmgtfy = hamper.plugins.commands:LetMeGoogleThatForYou',
            'lookup = hamper.plugins.dictionary:Lookup',
            'ponies = hamper.plugins.friendly:OmgPonies',
            'quit = hamper.plugins.commands:Quit',
            'quotes = hamper.plugins.quotes:Quotes',
            'remindme = hamper.plugins.remindme:Reminder',
            'rot13 = hamper.plugins.commands:Rot13',
            'roulette = hamper.plugins.roulette:Roulette',
            'sed = hamper.plugins.commands:Sed',
            'seen = hamper.plugins.seen:Seen',
            'suggest = hamper.plugins.suggest:Suggest',
            'timez = hamper.plugins.timez:Timez',
            'tinyurl = hamper.plugins.tinyurl:Tinyurl',
            'whatwasthat = hamper.plugins.whatwasthat:WhatWasThat',
            'yesno = hamper.plugins.questions:YesNoPlugin',
        ],
    },
)
