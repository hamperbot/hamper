import re
import random

from zope.interface import implements, Interface, Attribute

from hamper.IHamper import IPlugin


class Plugin(object):

    implements(IPlugin)

    name = 'Generic Plugin'
    onlyDirected = True
    caseSensitive = False
    regex = ''
    priority = 0

    def __call__(self, commander, options):
        return True


class Friendly(Plugin):
    """Be polite. When people say hello, response."""

    name = 'Friendly'
    regex = '.*'
    priority = 2

    def __init__(self):
        self.greetings = ['hi', 'hello', 'hey']

    def __call__(self, commander, options):
        if options['message'].strip() in self.greetings:
            commander.say('{0} {1[user]}'
                .format(random.choice(self.greetings), options))
            return False

        return True


class QuitCommand(Plugin):
    """Know when hamper isn't wanted."""

    name = 'Quit'
    regex = 'go away'

    def __call__(self, commander, options):
        commander.say('Bye!')
        commander.quit()


class OmgPonies(Plugin):
    """The classics never die."""

    name = 'OMG!!! Ponies!!!'
    regex = r'.*pon(y|ies).*'
    onlyDirected = False

    def __call__(self, commander, options):
        commander.say('OMG!!! PONIES!!!')

class Sed(Plugin):
    """To be honest, I feel strange in channels that don't have this."""

    name = 'sed'
    regex = r'^!s/(.*)/(.*)/(g?i?)'
    onlyDirected = False
    priority = -1

    def __call__(self, commander, opts):
        regex_opts = re.I if 'i' in opts['groups'][2] else 0
        usr_regex = re.compile(opts['groups'][0], regex_opts)
        usr_replace = opts['groups'][1]

        key = opts['channel'] if opts['channel'] else opts['user']

        if key not in commander.factory.history:
            commander.say('Who are you?! How did you get in my house?!')
            return

        for comm in reversed(commander.factory.history[key]):
            # Only look at our own, unless global was specified
            if 'g' not in opts['groups'][2] and comm['user'] != opts['user']:
                continue
            # Don't look at other sed commands
            if comm['message'].startswith('!s/'):
                continue
            if usr_regex.search(comm['message']):
                new_msg = usr_regex.sub(usr_replace, comm['message'])
                commander.say('{0} actually meant: {1}'
                        .format(comm['user'], new_msg))
                break
        else:
            commander.say("Sorry, I couldn't match /{0}/.".format(usr_regex.pattern))

class LetMeGoogleThatForYou(Plugin):
    """Link to the sarcastic letmegooglethatforyou.com."""

    name = 'lmgtfy'
    regex = '.*lmgtfy\s+(.*)'
    onlyDirected = False

    def __call__(self, commander, options):
        target = ''
        if options['target']:
            target = options['target'] + ': '
        commander.say(target + 'http://lmgtfy.com/?q=' + options['groups'][0])

lmgtfy = LetMeGoogleThatForYou()
sed = Sed()
omgponies = OmgPonies()
quit = QuitCommand()
hi = Friendly()
