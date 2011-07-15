import re

from hamper.commander import registerCommand


class Command(object):
    """Base class for a simple command."""

    onlyDirected = True
    caseSensitive = False
    regex = ''
    priority = 0

    def __call__(self, commander, options):
        pass


@registerCommand
class FriendlyCommand(Command):

    regex = 'hi'

    def __call__(self, commander, options):
        commander.say('Hello {0[user]}'.format(options))


@registerCommand
class QuitCommand(Command):

    regex = 'go away'

    def __call__(self, commander, options):
        commander.say('Bye!')
        commander.quit()


@registerCommand
class OmgPonies(Command):

    regex = r'.*pon(y|ies).*'
    onlyDirected = False

    def __call__(self, commander, options):
        commander.say('OMG PONIES!!!')

@registerCommand
class Sed(Command):

    regex = r'^!s/(.*)/(.*)/(g?i?)'
    onlyDirected = False
    priority = -1

    def __call__(self, commander, options):
        usr_regex = re.compile(options['groups'][0])
        usr_replace = options['groups'][1]

        key = options['channel'] if options['channel'] else options['user']

        for comm in commander.factory.history[key]:
            if usr_regex.search(comm['message']):
                new_msg = usr_regex.sub(usr_replace, comm['message'])
                commander.say('{0} actually meant: {1}'
                        .format(comm['user'], new_msg))

@registerCommand('.*lmgtfy\s+(.*)', False)
class LetMeGoogleThatForYou(object):
    def __call__(self, commander, user, message):
        regex = r'.*lmgtfy\s+(.*)\s*'
        match = re.match(regex, message, re.IGNORECASE).groups()[0]
        commander.say('http://lmgtfy.com/?q=' + match)

