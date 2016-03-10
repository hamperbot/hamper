import logging as _logging

from hamper.interfaces import Command, ChatCommandPlugin


log = _logging.getLogger('hamper.commands.help')


class Help(ChatCommandPlugin):
    """Provide an interface to get help on commands."""

    name = 'help'

    _command_cache = []

    def __init__(self, *args, **kwargs):
        super(Help, self).__init__(*args, **kwargs)
        self._command_cache = []

    @classmethod
    def helpful_commands(cls, bot):
        commands = set()
        for plugin in bot.factory.loader.plugins:
            if (hasattr(plugin, 'name') and hasattr(plugin, 'short_desc')
                    and hasattr(plugin, 'long_desc')):
                commands.add(plugin)

            commands.update(plugin.commands)

        for cmd in commands:
            if getattr(cmd, 'short_desc', None) is not None:
                yield cmd

    class HelpMainMenu(Command):
        name = 'help'
        regex = 'help$'

        short_desc = 'help [command] - Show help for commands.'
        long_desc = ('For detailed help on a command, say "!help <command>". '
                     'Some commands may not be listed. If you think they '
                     'should, poke the plugin author.')

        def command(self, bot, comm, groups):
            commands = Help.helpful_commands(bot)
            response = ['Available commands']
            for command in commands:
                response.append('{0.short_desc}'.format(command))
            response = '\n'.join(response)

            bot.msg(comm['user'], response)

    class HelpCommand(Command):
        name = 'help.individual'
        regex = 'help (.*)$'

        def command(self, bot, comm, groups):
            search = groups[0]

            commands = Help.helpful_commands(bot)
            try:
                command = [c for c in commands if c.name == search][0]
            except IndexError:
                bot.reply(comm, 'Unknown command')
                return

            if command.short_desc:
                bot.reply(comm, '{0.short_desc}'.format(command))
                if command.long_desc:
                    bot.reply(comm, '{0.long_desc}'.format(command))
