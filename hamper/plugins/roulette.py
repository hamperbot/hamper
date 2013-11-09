import random
import re
from datetime import datetime

from hamper.interfaces import ChatPlugin


class Roulette(ChatPlugin):
    """Feeling lucky? !roulette to see how lucky"""

    name = 'roulette'
    priority = 2

    def message(self, bot, comm):
        if not comm['directed'] and comm['pm']:
            return

        if re.match("roulette$", comm['message'], re.I):
            dice = random.randint(1,6)
            if dice == 6:
                bot.kick(comm["channel"], comm["user"], "You shot yourself!")

roulette = Roulette()
