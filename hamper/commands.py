from hamper.commander import registerCommand


class Command(object):
    """Base class for a simple command."""

    onlyDirected = True
    caseSensitive = False
    regex = ''

    def __call__(self, commander, sender, target, message):
        pass


@registerCommand
class FriendlyCommand(Command):

    regex = 'hi'

    def __call__(self, commander, sender, target, message):
        commander.say('Hello {0}'.format(sender))


@registerCommand
class QuitCommand(Command):

    regex = 'go away'

    def __call__(self, commander, sender, target, message):
        commander.say('Bye!')
        commander.quit()


@registerCommand
class OmgPonies(Command):

    regex = r'.*pon(y|ies).*'
    onlyDirected = False

    def __call__(self, commander, sender, target, message):
        commander.say('OMG PONIES!!!')
