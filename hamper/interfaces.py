import re

from zope.interface import implements, Interface, Attribute
from zope.interface.tests.test_verify import verifyClass
from zope.interface.exceptions import DoesNotImplement


class IPlugin(Interface):
    """Interface for a plugin.."""

    name = Attribute('Human readable name for the plugin.')
    priority = Attribute('Priority of plugins. High numbers are called first')

    def setup(factory):
        """
        Called when the factory loads the plugin.
        """

    def process(bot, comm):
        """
        Called when a matching message comes in to the bot.

        Return `True` if execution of plugins should stop after this. A return
        value of `False` or no return value (implicit `None`) will cause the
        next plugin to be called.
        """


class Plugin(object):
    """
    Base class for a plugin.

    If any of a classes children are Command classes, automatically call out to
    them.
    """
    implements(IPlugin)

    priority = 0

    def __init__(self):
        self.commands = []
        for name in dir(self):
            cls = getattr(self, name)
            try:
                if verifyClass(ICommand, cls):
                    print "Loading command {0}".format(cls)
                    self.commands.append(cls())
            except (DoesNotImplement, TypeError, AttributeError):
                pass

    def setup(self, factory):
        pass

    def process(self, bot, comm):
        for cmd in self.commands:
            stop = cmd.process(bot, comm)
            if stop:
                return stop


class ICommand(Interface):
    """Interface for a command."""

    regex = Attribute('The regex to trigger this command for.')
    caseSensitive = Attribute("The case sensitivity of the trigger regex.")
    onlyDirected = Attribute("Only respond to command directed at the bot.")

    def process(bot, comm):
        """Chooses whether or not to trigger the command."""

    def command(bot, comm, groups):
        """This function gets called when the command is triggered."""


class Command(object):
    """
    A convenience wrapper to implement a single command.

    To use it, define a clas that inherits from Command inside a Plugin.
    """
    implements(ICommand)

    caseSensitive = False
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
