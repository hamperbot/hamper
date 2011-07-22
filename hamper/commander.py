import sys
import re
from collections import deque
import yaml

from twisted.words.protocols import irc
from twisted.internet import protocol, reactor

from bravo.plugin import retrieve_plugins

from hamper.IHamper import IPlugin


class CommanderProtocol(irc.IRCClient):
    """Runs the IRC interactions, and calls out to plugins."""

    def _get_nickname(self):
        return self.factory.nickname

    nickname = property(_get_nickname)

    def signedOn(self):
        self.join(self.factory.channel)
        print "Signed on as %s." % (self.nickname,)

    def joined(self, channel):
        print "Joined %s." % (channel,)

    def privmsg(self, user, channel, msg):
        print channel, user, msg

        """On message received (from channel or user)."""
        if not user:
            # ignore server messages
            return

        directed = msg.startswith(self.nickname)
        # This monster of a regex extracts msg and target from a message, where
        # the target may not be there.
        target, msg = re.match(
            r'^(?:([a-z_\-\[\]\\^{}|`][a-z0-9_\-\[\]\\^{}|`]*)[:,] )? *(.*)$',
            msg).groups()

        if user:
            user, mask = user.split('!', 1)
        else:
            mask = ''

        comm = {
            'user': user,
            'mask': mask,
            'target': target,
            'message': msg,
            'channel': channel,
        }

        matchedPlugins = []
        for cmd in self.factory.plugins:
            match = cmd.regex.match(msg)
            if match and (directed or (not cmd.onlyDirected)):
                matchedPlugins.append((match, cmd))

        # High priority plugins first
        matchedPlugins.sort(key=lambda x: x[1].priority, reverse=True)

        for match, cmd in matchedPlugins:
            proc_comm = comm.copy()
            proc_comm.update({'groups': match.groups()})
            if not cmd(self, proc_comm):
                # The plugin asked us to not run any more.
                break

        key = channel if channel else user
        if not key in self.factory.history:
            self.factory.history[key] = deque(maxlen=100)
        self.factory.history[key].append(comm)

        # We can't remove/add plugins while we are in the loop, so do it here.
        while self.factory.pluginsToRemove:
            self.factory.plugins.remove(self.factory.pluginsToRemove.pop())

        while self.factory.pluginsToAdd:
            self.factory.registerPlugin(self.factory.pluginsToAdd.pop())

    def connectionLost(self, reason):
        reactor.stop()

    def say(self, msg):
        self.msg(self.factory.channel, msg)

    def removePlugin(self, plugin):
        self.factory.pluginsToRemove.add(plugin)

    def addPlugin(self, plugin):
        self.factory.pluginsToAdd.add(plugin)


class CommanderFactory(protocol.ClientFactory):

    protocol = CommanderProtocol

    def __init__(self, channel, nickname):
        self.channel = channel
        self.nickname = nickname

        self.history = {}

        self.plugins = set()
        # These are so plugins can be added/removed at run time. The
        # addition/removal will happen at a time when the set isn't being
        # iterated, so nothing breaks.
        self.pluginsToAdd = set()
        self.pluginsToRemove = set()

        for _, plugin in retrieve_plugins(IPlugin, 'hamper.plugins').items():
            self.registerPlugin(plugin)

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s)." % (reason)

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason,)

    def registerPlugin(self, plugin):
        """
        Registers a plugin.

        Also sets up the regex and other options for the plugin.
        """
        options = re.I if not plugin.caseSensitive else 0
        plugin.regex = re.compile(plugin.regex, options)

        self.plugins.add(plugin)
        print 'registered', plugin.name
