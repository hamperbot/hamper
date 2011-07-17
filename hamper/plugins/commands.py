import re

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

    name = 'Friendly'
    regex = 'hi'

    def __call__(self, commander, options):
        commander.say('Hello {0[user]}!'.format(options))


class QuitCommand(Plugin):

    name = 'Quit'
    regex = 'go away'

    def __call__(self, commander, options):
        commander.say('Bye!')
        commander.quit()


class OmgPonies(Plugin):

    name = 'OMG!!! Ponies!!!'
    regex = r'.*pon(y|ies).*'
    onlyDirected = False

    def __call__(self, commander, options):
        commander.say('OMG!!! PONIES!!!')

class Sed(Plugin):

    name = 'sed'
    regex = r'^!s/(.*)/(.*)/(g?i?)'
    onlyDirected = False
    priority = -1

    def __call__(self, commander, options):
        usr_regex = re.compile(options['groups'][0])
        usr_replace = options['groups'][1]

        key = options['channel'] if options['channel'] else options['user']

        for comm in reversed(commander.factory.history[key]):
            if usr_regex.search(comm['message']):
                new_msg = usr_regex.sub(usr_replace, comm['message'])
                commander.say('{0} actually meant: {1}'
                        .format(comm['user'], new_msg))
                break;

class LetMeGoogleThatForYou(Plugin):

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
