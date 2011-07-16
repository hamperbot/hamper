from zope.interface import implements, Interface, Attribute


class ICommand(Interface):
    """Interface for a command.."""

    name = Attribute('Human readable name for the plugin.')
    onlyDirected = Attribute('Only respond to messages directed at the bot.')
    caseSensitive = Attribute('Compile the regex to be caseSensitive if True.')
    regex = Attribute('What messages the command will be called for.')
    priority = Attribute('Higher numbers are called first.')

    def __call__(commander, options):
        """
        Called when a matching message comes in to the bot.

        Return `True` if the next command should be called, when there are
        multiple commands with the same priority. Returning `False` or not
        returing a value will cause execution to stop.
        """
