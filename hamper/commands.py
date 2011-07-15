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
