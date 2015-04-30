import logging

from hamper.interfaces import IPlugin, Command, ChatCommandPlugin

import twisted


log = logging.getLogger('hamper.plugins.plugin_utils')


class PluginUtils(ChatCommandPlugin):

    name = 'plugins'
    priority = 0

    @classmethod
    def get_plugins(cls, bot):
        all_plugins = set()
        for kind, plugins in bot.factory.loader.plugins.items():
            all_plugins.update(plugins)
        return all_plugins

    class ListPlugins(Command):
        regex = r'^plugins?(?: list)?$'

        name = 'plugins'
        short_desc = 'plugins subcommand - See extended help for more details.'
        long_desc = ('Manipulate plugins\n'
                     'list - List all loaded plugins\n'
                     'reload name - Reload a plugin by name.\n'
                     'unload name - Unload a plugin by name.\n'
                     'load name - Load a plugin by name.\n')

        def command(self, bot, comm, groups):
            """Reply with a list of all currently loaded plugins."""
            plugins = PluginUtils.get_plugins(bot)
            names = ', '.join(p.name for p in plugins)
            bot.reply(comm, 'Loaded Plugins: {0}.'.format(names))
            return True

    class LoadPlugin(Command):
        regex = r'^plugins? load (.*)$'

        def command(self, bot, comm, groups):
            """Load a named plugin."""
            name = groups[0]
            plugins = PluginUtils.get_plugins(bot)
            matched_plugins = [p for p in plugins if p.name == name]
            if len(matched_plugins) != 0:
                bot.reply(comm, "%s is already loaded." % name)
                return False

            # Fun fact: the fresh thing is just a dummy. It just can't be None
            new_plugin = twisted.plugin.retrieve_named_plugins(
                IPlugin, [name], 'hamper.plugins', {'fresh': True})[0]

            bot.factory.loader.registerPlugin(new_plugin)
            bot.reply(comm, 'Loading {0}.'.format(new_plugin))
            return True

    class UnloadPlugin(Command):
        regex = r'^plugins? unload (.*)$'

        def command(self, bot, comm, groups):
            """Unload a named plugin."""
            name = groups[0]
            plugins = PluginUtils.get_plugins(bot)
            matched_plugins = [p for p in plugins if p.name == name]
            if len(matched_plugins) == 0:
                bot.reply(comm, "I can't find a plugin named {0}!"
                                .format(name))
                return False

            target_plugin = matched_plugins[0]

            bot.factory.loader.removePlugin(target_plugin)
            bot.reply(comm, 'Unloading {0}.'.format(target_plugin))
            return True
