import sys
import re
from collections import deque
import traceback

import yaml
from twisted.words.protocols import irc
from twisted.internet import protocol, reactor
import sqlalchemy
from sqlalchemy import orm
from bravo.plugin import retrieve_plugins

from hamper.interfaces import IPlugin


class CommanderProtocol(irc.IRCClient):
    """Interacts with a single server, and delegates to the plugins."""

    ##### Properties #####
    @property
    def nickname(self):
        return self.factory.nickname

    @property
    def db(self):
        return self.factory.db

    ##### Twisted events #####

    def signedOn(self):
        """Called after successfully signing on to the server."""
        print "Signed on as %s." % (self.nickname,)
        for c in self.factory.channels:
            self.join(c)

    def joined(self, channel):
        """Called after successfully joining a channel."""
        print "Joined {0}.".format(channel)

    def privmsg(self, user, channel, msg):
        """Called when a message is received from a channel or user."""
        print channel, user, msg

        if not user:
            # ignore server messages
            return

        # This monster of a regex extracts msg and target from a message, where
        # the target may not be there, and the target is a valid irc name.
        # Valid ways to target someone are "<nick>: ..." and "<nick>, ..."
        target, msg = re.match(
            r'^(?:([a-z_\-\[\]\\^{}|`]' # First letter can't be a number
            '[a-z0-9_\-\[\]\\^{}|`]*)'  # The rest can be many things
            '[:,] )? *(.*)$',           # The actual message
            msg, re.I).groups()

        pm = channel == self.nickname
        if target:
            directed = target.lower() == self.nickname.lower()
        else:
            directed = False
        if msg.startswith('!'):
            msg = msg[1:]
            directed = True

        try:
            user, mask = user.split('!', 1)
        except:
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

        self.dispatch(comm)

        if not channel in self.factory.history:
            self.factory.history[channel] = deque(maxlen=100)
        self.factory.history[channel].append(comm)

    def connectionLost(self, reason):
        """Called when the connection is lost to the server."""
        self.factory.db.commit()
        reactor.stop()

    ##### Hamper specific functions. #####

    def dispatch(self, comm):
        """Take a comm that has been parsed and dispatch it to plugins."""

        # Plugins are already sorted by priority
        stop = False
        for plugin in self.factory.plugins:
            # If a plugin throws an exception, we should catch it gracefully.
            try:
                stop = plugin.process(self, comm)
                if stop:
                    break
            except:
                traceback.print_exc()

    def removePlugin(self, plugin):
        print("Unloading %r" % plugin)
        self.factory.plugins.remove(plugin)

    def addPlugin(self, plugin):
        print("Loading %r" % plugin)
        self.factory.registerPlugin(plugin)

    def leaveChannel(self, channel):
        """Leave the specified channel."""
        # For now just quit.
        self.quit()

    def reply(self, comm, message):
        if comm['pm']:
            self.msg(comm['user'], message)
        else:
            self.msg(comm['channel'], message)


class CommanderFactory(protocol.ClientFactory):

    protocol = CommanderProtocol

    def __init__(self, config):
        self.channels = config['channels']
        self.nickname = config['nickname']

        self.history = {}
        self.plugins = []
        # These are so plugins can be added/removed at run time. The
        # addition/removal will happen at a time when the list isn't being
        # iterated, so nothing breaks.
        self.pluginsToAdd = []
        self.pluginsToRemove = []

        if 'db' in config:
            print('Loading db from config: ' + config['db'])
            self.db_engine = sqlalchemy.create_engine(config['db'])
        else:
            print('Using in-memory db')
            self.db_engine = sqlalchemy.create_engine('sqlite:///:memory:')
        DBSession = orm.sessionmaker(self.db_engine)
        self.db = DBSession()

        for _, plugin in retrieve_plugins(IPlugin, 'hamper.plugins').items():
            if plugin.name in config['plugins']:
                self.registerPlugin(plugin)

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s)." % (reason)

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason,)

    def registerPlugin(self, plugin):
        """
        Registers a plugin.
        """
        plugin.setup(self)
        self.plugins.append(plugin)
        self.plugins.sort()
        print 'registered plugin', plugin.name
