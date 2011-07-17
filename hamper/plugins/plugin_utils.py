from zope.interface import implements, Interface, Attribute

from bravo import plugin

from hamper.plugins.commands import Plugin
from hamper.IHamper import IPlugin


class PluginUtils(Plugin):

    name = 'Plugin Utils'
    regex = '^plugins?(.*)$'

    def __call__(self, commander, options):

        args = options['groups'][0].split(' ')
        args = [a.strip() for a in args]
        args = [a for a in args if a]

        dispatch = {
            'list': self.listPlugins,
            'reload': self.reloadPlugin,
        }

        dispatch[args[0]](commander, args[1:])

    def listPlugins(self, commander, args):
        """Reply with a list of all currently loaded plugins."""
        commander.say('Loaded Plugins: {0}.'.format(
            ', '.join([c.name for c in commander.factory.plugins])))

    def reloadPlugin(self, commander, args):
        """Reload a named plugin."""
        name = ' '.join(args)

        ps = commander.factory.plugins

        matched_plugins = [p for p in ps if p.name == name]
        if len(matched_plugins) == 0:
            commander.say("I can't find a plugin named %s!" % name)
            return

        target_plugin = matched_plugins[0]
        # Fun fact: the fresh thing is just a dummy. It just can't be None
        new_plugin = plugin.retrieve_named_plugins(IPlugin, [name],
                'hamper.plugins', {'fresh': True})[0]

        commander.removePlugin(target_plugin)
        commander.addPlugin(new_plugin)
        commander.say('Request reload of {0}.'.format(new_plugin))

plugin_utils = PluginUtils()
