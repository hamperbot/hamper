import re
import logging

from zope.interface import Interface, Attribute, implements

from hamper.interfaces import Command, ChatCommandPlugin


log = logging.getLogger('hamper.commands.help')


class IHelpfulCommand(Interface):
    """Interface for a command."""

    trigger = Attribute('The text string to tell the user to use to name '
                        'this command.')
    short_desc = Attribute('One line description of what a command does.')
    long_desc = Attribute('Longer description of what a command does.')


class Help(ChatCommandPlugin):
    """Provide an interface to get help on commands."""

    name = 'help'

    _command_cache = []

    def __init__(self, *args, **kwargs):
        super(Help, self).__init__(*args, **kwargs)
        self._command_cache = []

    @classmethod
    def is_helpful(self, command):
        return IHelpfulCommand(command, None) is not None

    @classmethod
    def helpful_commands(cls, bot):
        if cls._command_cache:
            return cls._command_cache

        cls._command_cache = []
        for kind, plugins in bot.factory.plugins.items():
            for plugin in plugins:
                cls._command_cache.extend(plugin.commands)

        cls._command_cache = filter(cls.is_helpful, cls._command_cache)
        return cls._command_cache

    class HelpMainMenu(Command):
        name = 'help'
        regex = 'help$'

        implements(IHelpfulCommand)
        trigger = 'help [command]'
        short_desc = 'Show help for commands.'
        long_desc = ('For detailed help on a command, say "!help command". '
                      'Some commands may not be listed. If you think they '
                      'should, poke the plugin author.')

        def command(self, bot, comm, groups):
            commands = Help.helpful_commands(bot)
            response = ['Available commands']
            for command in commands:
                response.append('{0.name} - {0.short_desc}'.format(command))
            response = '\n'.join(response)

            bot.reply(comm, response)

    class HelpCommand(Command):
        name = 'help.individual'
        regex = 'help (.*)$'

        def command(self, bot, comm, groups):
            search = groups[0]

            commands = Help.helpful_commands(bot)
            try:
                command = [c for c in commands if c.name == search][0]
            except IndexError:
                comm.reply(comm, 'Unknown command')
                return

            bot.reply(comm, '{0.name} - {0.short_desc}\n{0.long_desc}'
                            .format(command))
