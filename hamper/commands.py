import re

from zope.interface import implements, Interface, Attribute

from hamper.commander import CommanderFactory

class ICommand(Interface):
    """Interface for a command.."""

    onlyDirected = Attribute('Only respond to messages directed at the bot.')
    caseSensitive = Attribute('Compile the regex to be caseSensitive if True.')
    regex = Attribute('What messages the command will be called for.')
    priority = Attribute('Higher numbers are called first.')

    def __call__(self, commander, options):
        """
        Called when a matching message comes in to the bot.

        Return `True` if the next command should be called, when there are
        multiple commands with the same priority. Returning `False` or not
        returing a value will cause execution to stop.
        """


class Command(object):
    implements(ICommand)

    onlyDirected = True
    caseSensitive = False
    regex = ''
    priority = 0

    def __call__(self, commander, options):
        return True

@CommanderFactory.registerCommand
class FriendlyCommand(Command):

    regex = 'hi'

    def __call__(self, commander, options):
        commander.say('Hello {0[user]}'.format(options))


@CommanderFactory.registerCommand
class QuitCommand(Command):

    regex = 'go away'

    def __call__(self, commander, options):
        commander.say('Bye!')
        commander.quit()


@CommanderFactory.registerCommand
class OmgPonies(Command):

    regex = r'.*pon(y|ies).*'
    onlyDirected = False

    def __call__(self, commander, options):
        commander.say('OMG PONIES!!!')

@CommanderFactory.registerCommand
class Sed(Command):

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

@CommanderFactory.registerCommand
class LetMeGoogleThatForYou(Command):

    regex = '.*lmgtfy\s+(.*)'
    onlyDirected = False

    def __call__(self, commander, options):
        target = ''
        if options['target']:
            target = options['target'] + ': '
        commander.say(target + 'http://lmgtfy.com/?q=' + options['groups'][0])
