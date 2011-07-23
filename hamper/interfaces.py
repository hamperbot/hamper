import re

from zope.interface import implements, Interface, Attribute


class IPlugin(Interface):
    """Interface for a plugin.."""

    name = Attribute('Human readable name for the plugin.')
    priority = Attribute('Priority of plugins. High numbers are called first')

    def process(bot, comm):
        """
        Called when a matching message comes in to the bot.

        Return `True` if execution of plugins should stop after this. A return
        value of `False` or no return value (implicit `None`) will cause the
        next plugin to be called.
        """


class Command(object):
    """Specialized plugin to implement a simple command"""
    implements(IPlugin)

    priority = 0

    caseSensitive = False
    regex = ''
    onlyDirected = True

    def __init__(self):
        if type(self.regex) == str:
            opts = 0 if self.caseSensitive else re.I
            self.regex = re.compile(self.regex, opts)

    def process(self, bot, comm):
        if self.onlyDirected and not comm['directed']:
            return
        match = self.regex.match(comm['message'])
        if match:
            self.command(bot, comm, match.groups())
            return True

    def command(self, bot, comm, groups):
        pass
