import sys
import re
from collections import deque
import yaml

from twisted.words.protocols import irc
from twisted.internet import protocol, reactor

from bravo.plugin import retrieve_plugins

from hamper.interfaces import IPlugin


class CommanderProtocol(irc.IRCClient):
    """Interacts with a single server, and delegates to the plugins."""

    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    def _get_db(self):
        return self.factory.db
    db = property(_get_db)

    def signedOn(self):
        self.join(self.factory.channel)
        print "Signed on as %s." % (self.nickname,)

    def joined(self, channel):
        print "Joined %s." % (channel,)

    def privmsg(self, user, channel, msg):
        """I received a message."""
        print channel, user, msg

        if not user:
            # ignore server messages
            return

        pm = channel == self.nickname
        directed = msg.startswith(self.nickname) or pm
        if msg.startswith('!'):
            msg = msg[1:]
            directed = True

        # This monster of a regex extracts msg and target from a message, where
        # the target may not be there, and the target is a valid irc name.  A
        # valid nickname consists of letters, numbers, _-[]\^{}|`, and cannot
        # start with a number. Valid ways to target someone are "<nick>: ..."
        # and "<nick>, ..."
        target, msg = re.match(
            r'^(?:([A-Za-z_\-\[\]\\^{}|`][A-Za-z0-9_\-\[\]\\^{}|`]*)[:,] )? *(.*)$',
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
            'directed': directed,
            'pm': pm,
        }

        # Plugins are already sorted by priority
        for plugin in self.factory.plugins:
            stop = plugin.process(self, comm)
            if stop:
                break

        #matchedPlugins = []
        #for cmd in self.factory.plugins:
        #    match = cmd.regex.match(msg)
        #    if match and (directed or (not cmd.onlyDirected)):
        #        matchedPlugins.append((match, cmd))

        ## High priority plugins first
        #matchedPlugins.sort(key=lambda x: x[1].priority, reverse=True)

        #for match, cmd in matchedPlugins:
        #    proc_comm = comm.copy()
        #    proc_comm.update({'groups': match.groups()})
        #    if not cmd(self, proc_comm):
        #        # The plugin asked us to not run any more.
        #        break

        if not channel in self.factory.history:
            self.factory.history[channel] = deque(maxlen=100)
        self.factory.history[channel].append(comm)

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
        self.factory.pluginsToRemove.append(plugin)

    def addPlugin(self, plugin):
        self.factory.pluginsToAdd.append(plugin)

    def leaveChannel(self, channel):
        """Leave the specified channel."""
        # For now just quit.
        self.quit()


class CommanderFactory(protocol.ClientFactory):

    protocol = CommanderProtocol

    def __init__(self, channel, nickname):
        self.channel = channel
        self.nickname = nickname

        self.history = {}

        self.plugins = []
        # These are so plugins can be added/removed at run time. The
        # addition/removal will happen at a time when the list isn't being
        # iterated, so nothing breaks.
        self.pluginsToAdd = []
        self.pluginsToRemove = []

        for _, plugin in retrieve_plugins(IPlugin, 'hamper.plugins').items():
            self.registerPlugin(plugin)

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s)." % (reason)

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason,)

    def registerPlugin(self, plugin):
        """
        Registers a plugin.
        """
        self.plugins.append(plugin)
        self.plugins.sort()
        print 'registered plugin', plugin.name
