import re

from zope.interface import implements
from bravo import plugin

from hamper.interfaces import Command, ChatCommandPlugin, IPlugin


class PluginUtils(ChatCommandPlugin):

    name = 'plugins'
    priority = 0

    class ListPlugins(Command):
        regex = r'^plugins?(?: list)?$'

        def command(self, bot, comm, groups):
            """Reply with a list of all currently loaded plugins."""
            bot.reply(comm, 'Loaded Plugins: {0}.'.format(
                ', '.join([c.name for c in bot.factory.plugins])))
            return True

    class ReloadPlugins(Command):
        regex = r'^plugins? reload (.*)$'
        def command(self, bot, comm, groups):
            """Reload a named plugin."""
            name = groups[0]

            ps = bot.factory.plugins
            matched_plugins = [p for p in ps if p.name == name]
            if len(matched_plugins) == 0:
                bot.reply(comm, "I can't find a plugin named {0}!"
                    .format(name))
                return False

            target_plugin = matched_plugins[0]
            # Fun fact: the fresh thing is just a dummy. It just can't be None
            new_plugin = plugin.retrieve_named_plugins(IPlugin, [name],
                    'hamper.plugins', {'fresh': True})[0]

            bot.removePlugin(target_plugin)
            bot.addPlugin(new_plugin)
            bot.reply(comm, 'Reloading {0}.'.format(new_plugin))
            return True

    class LoadPlugin(Command):
        regex = r'^plugins? load (.*)$'
        def command(self, bot, comm, groups):
            """Load a named plugin."""
            name = groups[0]
            ps = bot.factory.plugins
            matched_plugins = [p for p in ps if p.name == name]
            if len(matched_plugins) != 0:
                bot.reply(comm, "%s is already loaded." % name)
                return False

            # Fun fact: the fresh thing is just a dummy. It just can't be None
            new_plugin = plugin.retrieve_named_plugins(IPlugin, [name],
                    'hamper.plugins', {'fresh': True})[0]

            bot.addPlugin(new_plugin)
            bot.reply(comm, 'Loading {0}.'.format(new_plugin))
            return True

    class UnloadPlugin(Command):
        regex = r'^plugins? unload (.*)$'
        def command(self, bot, comm, groups):
            """Unload a named plugin."""
            name = groups[0]
            ps = bot.factory.plugins
            matched_plugins = [p for p in ps if p.name == name]
            if len(matched_plugins) == 0:
                bot.reply(comm, "I can't find a plugin named {0}!"
                    .format(name))
                return False

            target_plugin = matched_plugins[0]

            bot.removePlugin(target_plugin)
            bot.reply(comm, 'Unloading {0}.'.format(target_plugin))
            return True


plugin_utils = PluginUtils()
