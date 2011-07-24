import random
import re
from datetime import datetime

from zope.interface import implements

from hamper.interfaces import IPlugin


class Friendly(object):
    """Be polite. When people say hello, response."""
    implements(IPlugin)

    name = 'friendly'
    priority = 2

    def setup(self, factory):
        self.greetings = ['hi', 'hello', 'hey']

    def process(self, bot, comm):
        if not comm['directed']:
            return

        if comm['message'].strip() in self.greetings:
            bot.say('{0} {1[user]}'
                .format(random.choice(self.greetings), comm))
            return True


class OmgPonies(object):
    """The classics never die."""
    implements(IPlugin)

    name = 'ponies'
    priority = 3

    cooldown = 30 #seconds

    def setup(self, factory):
        self.last_pony_time = datetime.now()
        pass

    def process(self, bot, comm):
        if re.match(r'.*pon(y|ies).*', comm['message'], re.I):
            now = datetime.now()
            since_last_pony = now - self.last_pony_time
            if since_last_pony.total_seconds() >= self.cooldown:
                bot.say('OMG!!! PONIES!!!')
                self.last_pony_time = now
            else:
                print('too many ponies')

        # Always let the other plugins run
        return False


friendly = Friendly()
omgponies = OmgPonies()
