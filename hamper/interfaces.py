import logging
import re

from zope.interface import implements, Interface, Attribute
from zope.interface.exceptions import DoesNotImplement
from zope.interface.declarations import implementedBy

from twisted.plugin import IPlugin

log = logging.getLogger('hamper.interfaces')


class BaseInterface(Interface):
    """Interface for a plugin.."""

    name = Attribute('Human readable name for the plugin.')

    def setup(factory):
        """Called when the factory loads the plugin."""


class Plugin(object):
    name = "genericplugin"
    dependencies = []
    implements(IPlugin)

    def __init__(self):
        self.commands = []

    def setup(self, factory):
        pass


class IChatPlugin(BaseInterface):
    """Interface for a chat plugin."""

    priority = Attribute('Priority of plugins. High numbers are called first')

    def message(bot, comm):
        """
        Called when a message comes in to the bot.

        Return `True` if execution of plugins should stop after this. A return
        value of `False` or no return value (implicit `None`) will cause the
        next plugin to be called.
        """


class ChatPlugin(Plugin):
    """Base class for a chat plugin."""
    implements(IChatPlugin)

    priority = 0

    def message(self, bot, comm):
        pass


class ChatCommandPlugin(ChatPlugin):
    """
    Helper class for a ChatCommand plugin

    If any of a classes children are Command classes, automatically call out to
    them.
    """

    def setup(self, *args, **kwargs):
        super(ChatCommandPlugin, self).setup(*args, **kwargs)

        for name in dir(self):
            cls = getattr(self, name)
            try:
                if ICommand in implementedBy(cls):
                    log.info("Loading command {0}".format(cls.__name__))
                    self.commands.append(cls(self))
            except (DoesNotImplement, TypeError, AttributeError):
                pass

    def message(self, bot, comm):
        super(ChatCommandPlugin, self).message(bot, comm)
        for cmd in self.commands:
            stop = cmd.message(bot, comm)
            if stop:
                return stop


class ICommand(BaseInterface):
    """Interface for a command."""

    name = Attribute('The name of the command, for code purposes.')
    regex = Attribute('The regex to trigger this command for.')
    caseSensitive = Attribute("The case sensitivity of the trigger regex.")
    onlyDirected = Attribute("Only respond to command directed at the bot.")

    def message(bot, comm):
        """Chooses whether or not to trigger the command."""

    def command(bot, comm, groups):
        """This function gets called when the command is triggered."""


class Command(object):
    """
    A convenience wrapper to implement a single command.

    To use it, define a clas that inherits from Command inside a Plugin.
    """
    implements(IPlugin, ICommand)

    caseSensitive = False
    onlyDirected = True

    def __init__(self, plugin):
        self.plugin = plugin
        if type(self.regex) == str:
            opts = 0 if self.caseSensitive else re.I
            self.regex = re.compile(self.regex, opts)

    def message(self, bot, comm):
        if self.onlyDirected and not comm['directed']:
            return
        match = self.regex.match(comm['message'])
        if match:
            self.command(bot, comm, match.groups())
            return True


class IPresencePlugin(BaseInterface):
    """A plugin that gets events about the bot joining and leaving channels."""

    def joined(bot, channel):
        """
        Called when I finish joining a channel.

        Channel has the starting character (# or &) intact.
        """

    def left(bot, channel):
        """
        Called when I have left a channel.

        Channel has the starting character (# or &) intact.
        """

    def signedOn(bot):
        """Called after successfully signing on to the server."""


class PresencePlugin(Plugin):
    implements(IPresencePlugin)

    def joined(self, bot, channel):
        pass

    def left(self, bot, channel):
        pass

    def signedOn(self, bot):
        pass


class IPopulationPlugin(BaseInterface):
    """A plugin that recieves events about the population of channels."""

    def userJoined(bot, user, channel):
        """Called when I see another user joinging a channel."""

    def userLeft(bot, user, channe):
        """Called when I see another user leaving a channel."""

    def userQuit(bot, user, quitMessage):
        """Called when I see another user disconnect from the network."""

    def userKicked(bot, kickee, channel, kicker, message):
        """Called when I see someone else being kicked from a channel."""

    def namesReply(bot, prefix, params):
        """Called when the server responds to a names request"""

    def namesEnd(bot, prefix, params):
        """Called when the server finishes responding to a names request"""


class PopulationPlugin(Plugin):
    implements(IPopulationPlugin)

    def userJoined(self, bot, user, channel):
        pass

    def userLeft(self, bot, user, channe):
        pass

    def userQuit(self, bot, user, quitMessage):
        pass

    def userKicked(self, bot, kickee, channel, kicker, message):
        pass

    def namesReply(self, bot, prefix, params):
        pass

    def namesEnd(self, bot, prefix, params):
        pass
