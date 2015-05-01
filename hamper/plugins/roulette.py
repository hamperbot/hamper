import random

from hamper.interfaces import ChatCommandPlugin, Command


class Roulette(ChatCommandPlugin):
    """Feeling lucky? !roulette to see how lucky"""

    name = 'roulette'
    priority = 0

    class Roulette(Command):
        '''Try not to die'''

        regex = r'^roulette$'

        name = 'roulette'
        short_desc = 'feeling lucky?'
        long_desc = "See how lucky you are, just don't bleed everywhere"

        def command(self, bot, comm, groups):
            if comm['pm']:
                return False

            dice = random.randint(1, 6)
            if dice == 6:
                bot.kick(comm["channel"], comm["user"], "You shot yourself!")
            else:
                bot.reply(comm, "*click*")

            return True
