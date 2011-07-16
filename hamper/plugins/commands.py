import re

from zope.interface import implements, Interface, Attribute

from hamper.IHamper import ICommand


class Command(object):

    implements(ICommand)

    name = 'Generic Command'
    onlyDirected = True
    caseSensitive = False
    regex = ''
    priority = 0

    def __call__(self, commander, options):
        return True

class FriendlyCommand(Command):

    implements(ICommand)

    name = 'Friendly'
    regex = 'hi'

    def __call__(self, commander, options):
        commander.say('Hello {0[user]}'.format(options))


class QuitCommand(Command):

    implements(ICommand)

    name = 'Quit'
    regex = 'go away'

    def __call__(self, commander, options):
        commander.say('Bye!')
        commander.quit()


class OmgPonies(Command):

    implements(ICommand)

    name = 'OMG!!! Ponies!!!'
    regex = r'.*pon(y|ies).*'
    onlyDirected = False

    def __call__(self, commander, options):
        commander.say('OMG!!! PONIES!!!')

class Sed(Command):

    implements(ICommand)

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

class LetMeGoogleThatForYou(Command):

    implements(ICommand)

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
hi = FriendlyCommand()
