import random
import re
from datetime import datetime

from hamper.interfaces import ChatPlugin


class Friendly(ChatPlugin):
    """Be polite. When people say hello, respond."""

    name = 'friendly'
    priority = 2

    def setup(self, factory):
        self.greetings = ['hi', 'hello', 'hey', 'sup', 'yo', 'hola', 'ping',
                          'pong']

    def message(self, bot, comm):
        if not comm['directed']:
            return

        if comm['message'].strip() in self.greetings:
            bot.reply(comm, '{0} {1[user]}'
                      .format(random.choice(self.greetings), comm))
            return True


class OmgPonies(ChatPlugin):
    """The classics never die."""

    name = 'ponies'
    priority = 3

    cooldown = 30  # Seconds

    def setup(self, factory):
        self.last_pony_time = datetime.now()

    def message(self, bot, comm):
        if re.match(r'.*pon(y|ies).*', comm['message'], re.I):
            now = datetime.now()
            since_last = now - self.last_pony_time
            since_last = since_last.seconds + 24 * 60 * 60 * since_last.days

            if since_last >= self.cooldown:
                bot.reply(comm, 'OMG!!! PONIES!!!')
                self.last_pony_time = now
            else:
                print('too many ponies')

        # Always let the other plugins run
        return False


class BotSnack(ChatPlugin):
    """Reward a good bot."""

    name = 'botsnack'
    priority = -1

    def setup(self, factory):
        self.rewards = {
            'botsnack': ['yummy', 'my favorite!'],
            'goodhamper': ['^_^', ':D'],
        }

    def message(self, bot, comm):
        if not comm['directed']:
            return
        slug = comm['message'].lower().replace(' ', '')
        for k, v in self.rewards.items():
            if k in slug:
                bot.reply(comm, random.choice(v))
                return True

        return False
