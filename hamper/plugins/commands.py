import re
import random

from zope.interface import implements, Interface, Attribute

from hamper.interfaces import Command


class QuitCommand(Command):
    """Know when hamper isn't wanted."""

    name = 'quit'
    regex = 'go away'

    def command(self, bot, comm, groups):
        bot.say('Bye!')
        bot.leaveChannel(comm['channel'])
        return True


class Sed(Command):
    """To be honest, I feel strange in channels that don't have this."""

    name = 'sed'
    regex = r's/(.*)/(.*)/(g?i?m?)'
    onlyDirected = False
    priority = -1

    def command(self, bot, comm, groups):
        options = groups[2]

        regex_opts = re.I if 'i' in options else 0
        usr_regex = re.compile(groups[0], regex_opts)
        usr_replace = groups[1]

        count = 0 if 'g' in options else 1

        key = comm['channel']
        if key not in bot.factory.history:
            bot.say('Who are you?! How did you get in my house?!')
            return

        for hist in reversed(bot.factory.history[key]):
            # Only look at our own if only-me was specified
            if 'm' in options and hist['user'] != comm['user']:
                continue
            # Don't look at other sed commands
            if hist['directed'] and hist['message'].startswith('s/'):
                continue

            if usr_regex.search(hist['message']):
                new_msg = usr_regex.sub(usr_replace, hist['message'], count)
                bot.say('{0} actually meant: {1}'
                        .format(hist['user'], new_msg))
                break
        else:
            bot.say("Sorry, I couldn't match /{0}/.".format(usr_regex.pattern))

class LetMeGoogleThatForYou(Command):
    """Link to the sarcastic letmegooglethatforyou.com."""

    name = 'lmgtfy'
    regex = '^lmgtfy\s+(.*)'
    onlyDirected = False

    def command(self, bot, comm, groups):
        target = ''
        if comm['target']:
            target = comm['target'] + ': '
        args = groups[0].replace(' ', '+')
        bot.say(target + 'http://lmgtfy.com/?q=' + args)

lmgtfy = LetMeGoogleThatForYou()
sed = Sed()
quit = QuitCommand()
