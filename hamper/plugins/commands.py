import logging
import re
import random
from sre_constants import error as RegexError

from hamper.interfaces import Command, ChatCommandPlugin


log = logging.getLogger('hamper.plugins')


class Quit(ChatCommandPlugin):
    """Know when hamper isn't wanted."""
    name = 'quit'

    class QuitCommand(Command):
        regex = 'quit'

        def command(self, bot, comm, groups):
            if comm['pm']:
                bot.msg(comm['channel'], "You can't do that from PM.")
                return False

            bot.reply(comm, 'Bye!')
            bot.quit()
            return True


class Sed(ChatCommandPlugin):
    """To be honest, I feel strange in channels that don't have this."""
    name = 'sed'
    priority = -1

    def setup(self, loader):
        self.onlyDirected = loader.config.get('sed', {}).get('only-directed')
        super(Sed, self).setup(loader)

    class SedCommand(Command):
        name = 'sed'
        regex = r's/(.*)/(.*)/(.*)'
        onlyDirected = False

        short_desc = 's/find/replace/ - Perform sed style find and replace.'
        long_desc = ('Use like "s/foo/bar/" to search for "foo" and replace '
                     'it with "bar". \n'
                     'Flags: Add these flags to the end of the command:\n'
                     'm - Restrict the search to only your messages\n'
                     'i - Case insensitive searching.\n'
                     'g - Match an unlimited number of times.')

        def command(self, bot, comm, groups):
            if self.plugin.onlyDirected and not comm['directed']:
                return False
            usr_replace = groups[1]
            options = groups[2]
            regex_opts = re.I if 'i' in options else 0
            try:
                usr_regex = re.compile(groups[0], regex_opts)
            except RegexError:
                bot.reply(comm, 'Do you even lift?')
                return False

            g = 0 if 'g' in options else 1

            key = comm['channel']
            if key not in bot.factory.history:
                bot.reply(comm, 'Who are you?! How did you get in my house?!')
                return False

            for hist in reversed(bot.factory.history[key]):
                if 'm' in options and hist['user'] != comm['user']:
                    # Only look at the user's messages
                    continue

                # Don't look at other sed commands
                if 's/' in hist['raw_message']:
                    continue

                if usr_regex.search(hist['raw_message']):
                    try:
                        new_msg = usr_regex.sub(
                            usr_replace, hist['raw_message'], g
                        )
                    except RegexError:
                        bot.reply(comm, 'Do you even lift?')
                        return False
                    bot.reply(comm, '{0} actually meant: {1}'
                              .format(hist['user'], new_msg))
                    break
            else:
                bot.reply(comm, "Sorry, I couldn't match '{0}'."
                          .format(usr_regex.pattern))


class LetMeGoogleThatForYou(ChatCommandPlugin):
    """Link to the sarcastic letmegooglethatforyou.com."""
    name = 'lmgtfy'

    class LMGTFYCommand(Command):
        name = 'lmgtfy'
        regex = '^lmgtfy\s+(.*)'
        onlyDirected = False

        short_desc = 'lmgtfy - Show someone where to find something.'
        long_desc = ('This command will be triggered at the beginning of a '
                     'message to anyone, so you can use it like "Bob: lmgtfy '
                     'rtfm" to show Bob how to search for "rtfm".')

        def command(self, bot, comm, groups):
            target = ''
            if comm['target']:
                target = comm['target'] + ': '
            args = groups[0].replace(' ', '+')
            bot.reply(comm, target + 'http://lmgtfy.com/?q=' + args)


class Rot13(ChatCommandPlugin):
    """Encode secret messages."""
    name = 'rot13'

    class Rot13Command(Command):
        name = 'rot13'
        regex = '^rot13\s+(.*)'
        onlyDirected = False

        short_desc = 'rot13 - Encodes string using rot13 cipher.'
        long_desc = ('The rot13 cipher rotates every letter to the '
                     'other side of the alphabet. Applying it twice '
                     'returns the original string.\n'
                     'Example: !rot13 science yields fpvrapr'
                     ' and !rot13 fpvrapr yields science')

        def command(self, bot, comm, groups):
            target = ''
            if comm['target']:
                target = comm['target'] + ': '
            try:
                args = groups[0].encode('rot13')
                bot.reply(comm, target + args)
            except UnicodeDecodeError:
                bot.reply(
                    comm,
                    "It doesn't make sense to rot13 unicode characters"
                )


class Dice(ChatCommandPlugin):
    """Random dice rolls!"""
    name = 'dice'
    priority = 0

    def setup(self, *args, **kwargs):
        super(Dice, self).setup(*args, **kwargs)
        log.info('dice setup')

    @classmethod
    def roll(cls, num, sides, add):
        """Rolls a die of sides sides, num times, sums them, and adds add"""
        rolls = []
        for i in range(num):
            rolls.append(random.randint(1, sides))
        rolls.append(add)
        return rolls

    class DiceCommand(Command):
        name = 'dice'
        regex = '^(\d*)d(?:ice)?(\d*)\+?(\d*)$'
        onlyDirected = True

        short_desc = 'Dice - Roll dice by saying !XdY+Z.'
        long_desc = ('Use like XdY+Z to roll X Y sided dice and add Z. Any '
                     'number may be left off.\n'
                     'Example: "!1d20+5" to roll a single twenty sided die '
                     'and add 5 to the result. You don\'t have to direct '
                     'this to the bot.')

        def command(self, bot, com, groups):
            num, sides, add = groups

            if not num:
                num = 1
            else:
                num = int(num)

            if not sides:
                sides = 6
            else:
                sides = int(sides)

            if not add:
                add = 0
            else:
                add = int(add)

            result = Dice.roll(num, sides, add)
            output = '%s: You rolled %sd%s+%s and got ' % (com['user'], num,
                                                           sides, add)
            if len(result) < 11:
                # the last one is the constant to add
                for die in result[:-1]:
                    output += "%s, " % die
            else:
                output += "a lot of dice "

            output += "for a total of %s" % sum(result)

            bot.say(com['channel'], output)
