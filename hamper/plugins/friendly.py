import random
import re

from zope.interface import implements

from hamper.interfaces import IPlugin


class Friendly(object):
    """Be polite. When people say hello, response."""
    implements(IPlugin)

    name = 'friendly'
    priority = 2

    def __init__(self):
        self.greetings = ['hi', 'hello', 'hey']

    def process(self, bot, comm):
        if comm['message'].strip() in self.greetings:
            bot.say('{0} {1[user]}'
                .format(random.choice(self.greetings), comm))
            return True

        return False


class OmgPonies(object):
    """The classics never die."""
    implements(IPlugin)

    name = 'ponies'
    priority = 3

    def process(self, bot, comm):
        if re.match(r'.*pon(y|ies).*', comm['message']):
            bot.say('OMG!!! PONIES!!!')
        return False


friendly = Friendly()
omgponies = OmgPonies()
