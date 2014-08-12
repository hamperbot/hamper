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
    def toplevel_commands(cls, bot):
        commands = set()
        for kind, plugins in bot.factory.loader.plugins.items():
            for plugin in plugins:
                if (hasattr(plugin, 'name') and hasattr(plugin, 'short_desc')
                        and hasattr(plugin, 'long_desc')):
                    commands.add(plugin)

        for cmd in commands:
            if getattr(cmd, 'short_desc', None) is not None:
                yield cmd

    @classmethod
    def plugin_commands(cls, bot, plugin_name):
        commands = set()
        for kind, plugins in bot.factory.loader.plugins.items():
            for plugin in plugins:
                if plugin.name == plugin_name:
                    commands.update(plugin.commands)

        for command in commands:
            yield command

    class HelpMainMenu(Command):
        name = 'help'
        regex = 'help$'

        short_desc = 'help [command] - Show help for commands.'
        long_desc = ('For detailed help on a command, say "!help command". '
                     'Some commands may not be listed. If you think they '
                     'should, poke the plugin author.')

        def command(self, bot, comm, groups):
            commands = Help.toplevel_commands(bot)
            response = ['Available plugins']
            for command in commands:
                response.append(
                    '{0} - {1}'.format(command.name, command.short_desc)
                )
            response = '\n'.join(response)

            bot.reply(comm, response)

    class HelpCommand(Command):
        name = 'help.individual'
        regex = 'help (.*)$'

        def command(self, bot, comm, groups):
            search = groups[0]
            commands = Help.plugin_commands(bot, search)
            if not commands:
                bot.reply(comm, 'Unknown command')
                return

            print commands
            bot.reply(comm, 'Available commands for ' + search)
            for command in commands:
                print commands
                bot.reply(comm, '{0} - {1}'
                          .format(command.name, command.short_desc))
                if hasattr(command, 'long_desc'):
                    bot.reply(comm, '{0}   {1}'
                              .format(len(command.name) * ' ', command.long_desc))

help = Help()
