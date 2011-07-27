import re

from zope.interface import implements
from bravo import plugin

from hamper.interfaces import Command, IPlugin


class PluginUtils(Command):

    name = 'plugins'
    priority = 0
    regex = r'^plugins?\W+(.*)$'

    def command(self, bot, comm, groups):
        args = groups[0].split(' ')
        args = [a.strip() for a in args]
        args = [a for a in args if a]

        dispatch = {
            'list': self.listPlugins,
            'reload': self.reloadPlugin,
            'load': self.loadPlugin,
            'unload': self.unloadPlugin,
        }
        print args

        if len(args) == 0:
            self.listPlugins(bot, comm, *args)
            return True

        if args[0] in dispatch:
            dispatch[args[0]](bot, comm, *args)
            return True

    def listPlugins(self, bot, comm, *args):
        """Reply with a list of all currently loaded plugins."""
        bot.msg(comm['channel'], 'Loaded Plugins: {0}.'.format(
            ', '.join([c.name for c in bot.factory.plugins])))

    def reloadPlugin(self, bot, comm, *args):
        """Reload a named plugin."""
        name = ' '.join(args[1:])

        ps = bot.factory.plugins
        matched_plugins = [p for p in ps if p.name == name]
        if len(matched_plugins) == 0:
            bot.msg(comm['channel'], "I can't find a plugin named %s!" % name)
            return

        target_plugin = matched_plugins[0]
        # Fun fact: the fresh thing is just a dummy. It just can't be None
        new_plugin = plugin.retrieve_named_plugins(IPlugin, [name],
                'hamper.plugins', {'fresh': True})[0]

        bot.removePlugin(target_plugin)
        bot.addPlugin(new_plugin)
        bot.msg(comm['channel'], 'Reloading {0}.'.format(new_plugin))

    def loadPlugin(self, bot, comm, *args):
        """Load a named plugin."""
        name = ' '.join(args[1:])
t
        ps = bot.factory.plugins
        matched_plugins = [p for p in ps if p.name == name]
        if len(matched_plugins) != 0:
            bot.msg(comm['channel'], "%s is already loaded." % name)
            return

        new_plugin = plugin.retrieve_named_plugins(IPlugin, [name],
                'hamper.plugins', {'fresh': True})[0]
        bot.addPlugin(new_plugin)
        bot.msg(comm['channel'], 'Loading {0}.'.format(new_plugin))

    def unloadPlugin(self, bot, comm, *args):
        """Unload a named plugin."""
        name = ' '.join(args[1:])

        ps = bot.factory.plugins
        matched_plugins = [p for p in ps if p.name == name]
        if len(matched_plugins) == 0:
            bot.msg(comm['channel'], "I can't find a plugin named %s!" % name)
            return

        target_plugin = matched_plugins[0]

        bot.removePlugin(target_plugin)
        bot.msg(comm['channel'], 'Unloading {0}.'.format(new_plugin))


plugin_utils = PluginUtils()
