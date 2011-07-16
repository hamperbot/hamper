from zope.interface import implements, Interface, Attribute

from hamper.plugins.commands import Plugin


class PluginUtils(Plugin):

    names = 'Plugin Utils'
    regex = '^plugins?(.*)$'

    def __call__(self, commander, options):

        args = options['groups'][0].split(' ')
        args = [a.strip() for a in args]
        args = [a for a in args if a]
        commander.say('args: ' + repr(args))

        dispatch = {
            'list': self.listPlugins,
        }

        dispatch[args[0]](commander, args[1:])

    def listPlugins(self, commander, args):
        """Reply with a list of all currently loaded plugins."""
        commander.say('Loaded Plugins: {0}.'.format(
            ', '.join([c.name for c in commander.factory.commands])))

plugin_utils = PluginUtils()
