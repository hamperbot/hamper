import sys
import re

from collections import deque

from twisted.words.protocols import irc
from twisted.internet import protocol, reactor

class Commander(irc.IRCClient):

    commands = []

    def _get_nickname(self):
        return self.factory.nickname

    nickname = property(_get_nickname)

    def signedOn(self):
        self.join(self.factory.channel)
        print "Signed on as %s." % (self.nickname,)

    def joined(self, channel):
        print "Joined %s." % (channel,)

    def privmsg(self, user, channel, msg):
        """On message received (from channel or user)."""

        print user, msg

        if not user:
            # ignore server messages
            return


        directed = msg.startswith(self.nickname)
        # This monster of a regex extracts msg and target from a message, where
        # the target may not be there.
        target, msg = re.match(
            r'^(?:([a-z_\-\[\]\\^{}|`][a-z0-9_\-\[\]\\^{}|`]*)[:,] )? *(.*)$',
            msg).groups()

        user, mask = user.split('!', 1)

        comm = {
            'user': user,
            'mask': mask,
            'target': target,
            'message': msg,
            'channel': channel,
        }

        for cmd in Commander.commands:
            match = cmd.regex.match(msg)
            if match and (directed or (not cmd.onlyDirected)):
                comm.update({'groups': match.groups()})
                cmd(self, comm)

        key = channel if channel else user
        if not key in self.factory.history:
            self.factory.history[key] = deque(maxlen=100)
        self.factory.history[key].append(comm)


    def connectionLost(self, reason):
        reactor.stop()

    def say(self, msg):
        self.msg(self.factory.channel, msg)


class CommanderFactory(protocol.ClientFactory):

    protocol = Commander

    def __init__(self, channel, nickname='Hamper'):
        self.channel = channel
        self.nickname = nickname

        self.history = {}

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s)." % (reason)

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason,)


def registerCommand(Command):
    """Register a command with the Commander. To be used as a decorator."""
    options = re.I if not Command.caseSensitive else None
    Command.regex = re.compile(Command.regex, options)

    Commander.commands.append(Command())
    print 'registered', Command
