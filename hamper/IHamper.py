from zope.interface import implements, Interface, Attribute


class IPlugin(Interface):
    """Interface for a plugin.."""

    name = Attribute('Human readable name for the plugin.')
    onlyDirected = Attribute('Only respond to messages directed at the bot.')
    caseSensitive = Attribute('Compile the regex to be caseSensitive if True.')
    regex = Attribute('What messages the plugin will be called for.')
    priority = Attribute('Higher numbers are called first.')

    def __call__(commander, options):
        """
        Called when a matching message comes in to the bot.

        Return `True` if the next plugin should be called, when there are
        multiple plugins with the same priority. Returning `False` or not
        returing a value will cause execution to stop.
        """
