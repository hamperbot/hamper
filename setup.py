#!/usr/bin/env python2

from setuptools import setup, find_packages

from hamper import version

#requires = open('requirements.txt').read().split('\n')
#requires = [dep for dep in requires if 'psycopg' not in dep]
requires = []

setup(
    name='hamper',
    version=version.encode('utf8'),
    description='Yet another IRC bot',
    install_requires=requires,
    author='Mike Cooper',
    author_email='mythmon@gmail.com',
    url='https://www.github.com/hamperbot/hamper',
    packages=find_packages(),
    scripts=['scripts/hamper'],
    entry_points = {
        'hamperbot.plugins': [
                'karma = hamper.plugins.karma:Karma',
                'friendly = hamper.plugins.friendly:Friendly',
                'bitly = hamper.plugins.bitly:Bitly',
                'join_command = hamper.plugins.channel_utils.ChannelUtils:JoinCommand',
                'leave_command = hamper.plugins.channel_utils.ChannelUtils:LeaveCommand',
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
            ],
    },
)
