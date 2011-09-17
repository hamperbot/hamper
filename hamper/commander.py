import sys
import re
from collections import deque
import traceback
from fnmatch import fnmatch

import yaml
from twisted.words.protocols import irc
from twisted.internet import protocol, reactor
import sqlalchemy
from sqlalchemy import orm
from bravo.plugin import retrieve_named_plugins, verify_plugin

from hamper.interfaces import *


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

    def privmsg(self, raw_user, channel, raw_message):
        """Called when a message is received from a channel or user."""
        print channel, raw_user, raw_message

        if not raw_user:
            # ignore server messages
            return

        # This monster of a regex extracts msg and target from a message, where
        # the target may not be there, and the target is a valid irc name.
        # Valid ways to target someone are "<nick>: ..." and "<nick>, ..."
        target, message = re.match(
            r'^(?:([a-z_\-\[\]\\^{}|`]' # First letter can't be a number
            '[a-z0-9_\-\[\]\\^{}|`]*)'  # The rest can be many things
            '[:,] )? *(.*)$',           # The actual message
            raw_message, re.I).groups()

        pm = channel == self.nickname
        if target:
            directed = target.lower() == self.nickname.lower()
        else:
            directed = False
        if message.startswith('!'):
            message = message[1:]
            directed = True

        try:
            user, mask = raw_user.split('!', 1)
        except:
            user = raw_user
            mask = ''

        comm = {
            'raw_message': raw_message,
            'message': message,
            'raw_user': raw_user,
            'user': user,
            'mask': mask,
            'target': target,
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
        for plugin in self.factory.plugins['chat']:
            # If a plugin throws an exception, we should catch it gracefully.
            try:
                stop = plugin.message(self, comm)
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
        self.plugins = {}

        if 'db' in config:
            print('Loading db from config: ' + config['db'])
            self.db_engine = sqlalchemy.create_engine(config['db'])
        else:
            print('Using in-memory db')
            self.db_engine = sqlalchemy.create_engine('sqlite:///:memory:')
        DBSession = orm.sessionmaker(self.db_engine)
        self.db = DBSession()

        # Load all plugins mentioned in the config file. Allow globbing.
        plugins = retrieve_named_plugins(IPlugin, config['plugins'], 'hamper.plugins')
        for plugin in plugins:
            self.registerPlugin(plugin)

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s)." % (reason)

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason,)

    def registerPlugin(self, plugin):
        """
        Registers a plugin.
        """

        plugin_types = {
            "presence": IPresencePlugin,
            "chat": IChatPlugin,
            "population": IPopulationPlugin,
        }

        valid_types = ['baseplugin']
        for t, interface in plugin_types.iteritems():
            try:
                if t not in self.plugins:
                    self.plugins[t] = []
                self.plugins[t].append(verify_plugin(interface, plugin))
                self.plugins[t].sort()
                valid_types.append(t)
            except:
                pass

        plugin.setup(self)

        print 'registered plugin {0} as {1}'.format(plugin.name, valid_types)
