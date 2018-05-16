import random

from hamper.interfaces import ChatPlugin
from hamper.utils import ude

vowels = ['a','e','o','i','u', 'y']

unfunnies = [
    'chuckle',
    'funny',
    'hilarious',
    'giggle',
    'grin',
    'humor',
    'humour',
    'jest',
    'joke',
    'joking',
    'jolly',
    'laugh',
    'smile',
    'make fun',
    'making fun',
]

goods = [
    'great',
    'good',
    'grand',
    'jolly',
    'jovial',
    'magnificent',
    'marvelous',
    'splendid',
    'superb',
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

chuckles = [
    ' heh ',
    ' hah ',
    ' ha ',
    'teehee',
    'tee-hee-hee',
    ' lol ',
    '*snicker*',
    ' haha',
    'lmao',
    'rofl',
    'lmfao',
    'lollerskates',
    'lollercoasteer',
    'loltastic',
    'roflcopter',
    ' lul ',
    ' lel ',
    ' kek ',
    ':)',
    ':3',
]

class ManiacalPlugin(ChatPlugin):
    """Apparently robots 'laugh manically out of the blue' sometimes?"""
    # TODO: gendered laughter. Apparently girls say tee hee snicker snicker?
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

    def demurelaugh(self):
        return random.choice(chuckles) + random.choice(ends)

    def laughfor(self, bot, comm):
        if random.random() < .01:
            resp = self.makelaugh()
        else:
            resp = self.demurelaugh()
        resp += " " + random.choice(goods) + " " + random.choice(unfunnies)
        resp += random.choice(ends)
        if random.random() < .5:
            resp += ", " + comm['user']
        bot.reply(comm, '{0}: {1}'.format(comm['user'], resp))

    def laughalong(self, bot, comm):
        bot.reply(comm, random.choice(chuckles).strip() + random.choice(ends))

    def message(self, bot, comm):
        msg = ude(comm['message']).lower()
        for f in unfunnies:
            if f in msg:
                if comm['directed'] or random.random() > .6:
                    self.laughfor(bot, comm)
        for c in chuckles:
            if c in msg:
                if len(msg.strip()) < 6 or random.random() < .8:
                    self.laughalong()
        return False

