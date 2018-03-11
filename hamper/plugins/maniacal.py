import random
import re

from hamper.interfaces import ChatPlugin, Command
from hamper.utils import ude

vowels = ['a','e','o','i','u', 'y']

unfunnies = [
    'joke',
    'joking',
    'humor',
    'humour',
    'laugh',
    'funny',
    'giggle',
    'grin',
    'smile',
    'jest',
    'jolly',
]

goods = [
    'great',
    'good',
    'grand',
    'jolly',
    'splendid',
    'marvelous',
    'magnificent',
    'superb',
    'jovial',
]

ends = [
    '!',
    '.',
    '...',
    '?',
    '!!',
    '!!!',
    '',
]

class ManiacalPlugin(ChatPlugin):
    """Apparently robots 'laugh manically out of the blue' sometimes?"""

    name = 'maniacal'
    priority = 2

    def setup(self, *args):
        pass

    def startLaugh(self):
        s = random.random()
        if s < .2:
            return "MWA"
        if s < .4:
            return "BWA"
        if s < .45:
            return "  ..."
        return ""

    def midLaugh(self):
        syl = "h"
        if random.random() > .7:
            syl = "-h"
        if random.random() < .2:
            syl = " h"
        for v in vowels:
            if random.random() < .7:
                syl += v + v * int(random.random() * 4)
                break
        if random.random() < .5:
            syl = syl.upper()
        return syl

    def makelaugh(self):
        resp = self.startLaugh() + self.midLaugh()
        for i in range(10):
            if random.random() < .5:
                resp += self.midLaugh()
        resp += random.choice(ends)
        return resp

    def laughfor(self, bot, comm):
        resp = self.makelaugh()
        resp += " " + random.choice(goods) + " " + random.choice(unfunnies)
        if random.random() < .5:
            resp += ", " + comm['user']
        bot.reply(comm, '{0}: {1}'.format(comm['user'], resp))

    def message(self, bot, comm):
        msg = ude(comm['message'].strip()).lower()
        for f in unfunnies:
            if f in msg:
                self.laughfor(bot, comm)

        return False

