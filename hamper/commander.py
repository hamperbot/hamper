from bisect import insort
from collections import deque, namedtuple
import logging
import re
import traceback
from fnmatch import fnmatch

from twisted.words.protocols import irc
from twisted.internet import protocol, reactor
from twisted.plugin import getPlugins
from zope.interface import implementedBy
from zope.interface.verify import verifyObject
from zope.interface.exceptions import DoesNotImplement

import sqlalchemy
from sqlalchemy import orm

import hamper.config
import hamper.log
from hamper import plugins
from hamper.interfaces import (BaseInterface, IPresencePlugin, IChatPlugin,
                               IPopulationPlugin)


log = logging.getLogger('hamper')


def main():
    config = hamper.config.load()
    hamper.log.setup_logging()

    reactor.connectTCP(config['server'], config['port'],
                       CommanderFactory(config))
    reactor.run()


class CommanderProtocol(irc.IRCClient):
    """Interacts with a single server, and delegates to the plugins."""

    ##### Properties #####
    @property
    def nickname(self):
        return self.factory.nickname

    @property
    def db(self):
        return self.factory.loader.db

    ##### Twisted events #####

    def signedOn(self):
        """Called after successfully signing on to the server."""
        log.info("Signed on as %s.", self.nickname)
        self.dispatch('presence', 'signedOn')
        for c in self.factory.channels:
            self.join(*c)

    def joined(self, channel):
        """Called after successfully joining a channel."""
        print "Joined {0}.".format(channel)
        # ask for the current list of users in the channel
        self.dispatch('presence', 'joined', channel)

    def left(self, channel):
        """Called after leaving a channel."""
        print "Left {0}.".format(channel)
        self.dispatch('presence', 'left', channel)

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
            r'^(?:([a-z_\-\[\]\\^{}|`]'  # First letter can't be a number
            '[a-z0-9_\-\[\]\\^{}|`]*)'   # The rest can be many things
            '[:,] )? *(.*)$',            # The actual message
            raw_message, re.I).groups()

        pm = channel == self.nickname
        if target:
            if target.lower() == self.nickname.lower():
                directed = True
            else:
                directed = False
                message = '{0}: {1}'.format(target, message)
        else:
            directed = False
        if message.startswith('!'):
            message = message[1:]
            directed = True

        try:
            user, mask = raw_user.split('!', 1)
        except ValueError:
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

        self.dispatch('chat', 'message', comm)

        if not channel in self.factory.history:
            self.factory.history[channel] = deque(maxlen=100)
        self.factory.history[channel].append(comm)

    def connectionLost(self, reason):
        """Called when the connection is lost to the server."""
        self.factory.loader.db.session.commit()
        if reactor.running:
            reactor.stop()

    def userJoined(self, user, channel):
        """Called when I see another user joining a channel."""
        self.dispatch('population', 'userJoined', user, channel)

    def userLeft(self, user, channel):
        """Called when I see another user leaving a channel."""
        self.dispatch('population', 'userLeft', user, channel)

    def userQuit(self, user, quitmessage):
        """Called when I see another user quitting."""
        self.dispatch('population', 'userQuit', user, quitmessage)

    def userKicked(self, kickee, channel, kicker, message):
        """Called when I see another user get kicked."""
        self.dispatch('population', 'userKicked', kickee, channel, kicker,
                      message)

    def irc_RPL_NAMREPLY(self, prefix, params):
        """Called when the server responds to my names request"""
        self.dispatch('population', 'namesReply', prefix, params)

    def irc_RPL_ENDOFNAMES(self, prefix, params):
        """Called after the names request is finished"""
        self.dispatch('population', 'namesEnd', prefix, params)

    ##### Hamper specific functions. #####

    def dispatch(self, category, func, *args):
        """Take a comm that has been parsed and dispatch it to plugins."""

        self.factory.loader.runPlugins(category, func, self, *args)

    def reply(self, comm, message):
        message = message.encode('utf8')
        if comm['pm']:
            self.msg(comm['user'], message)
        else:
            self.msg(comm['channel'], message)

    def me(self, comm, message):
        message = message.encode('utf8')
        if comm['pm']:
            self.describe(comm['user'], message)
        else:
            self.describe(comm['channel'], message)


class CommanderFactory(protocol.ClientFactory):

    protocol = CommanderProtocol

    def __init__(self, config):
        self.channels = [c.split(' ', 1) for c in config['channels']]
        self.nickname = config['nickname']
        self.history = {}

        self.loader = PluginLoader()
        self.loader.config = config

        if 'db' in config:
            print('Loading db from config: ' + config['db'])
            db_engine = sqlalchemy.create_engine(config['db'])
        else:
            print('Using in-memory db')
            db_engine = sqlalchemy.create_engine('sqlite:///:memory:')
        DBSession = orm.sessionmaker(db_engine)
        session = DBSession()

        self.loader.db = DB(db_engine, session)

        # Load all plugins mentioned in the configuration. Allow globbing.
        config_matches = set()
        for plugin in getPlugins(BaseInterface, package=plugins):
            for pattern in config['plugins']:
                if fnmatch(plugin.name, pattern):
                    self.loader.registerPlugin(plugin)
                    config_matches.add(pattern)
                    break
        for pattern in config['plugins']:
            if pattern not in config_matches:
                log.warning('No plugin matched pattern "%s"', pattern)


    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s)." % (reason)
        # Reconnect
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason,)


class DB(namedtuple("DB", "engine, session")):
    """
    A small data structure that stores database information.
    """


class PluginLoader(object):
    """
    I am a repository for plugins.

    I understand how to load plugins and how to enumerate the plugins I've
    loaded. Additionally, I can store configuration data for plugins.

    Think of me as the piece of code that isolates plugin state from the
    details of the network.
    """

    def __init__(self):
        self.plugins = {
            'base_plugin': [],
            'presence': [],
            'chat': [],
            'population': [],
        }

    def registerPlugin(self, plugin):
        """Registers a plugin."""

        plugin_types = {
            'presence': IPresencePlugin,
            'chat': IChatPlugin,
            'population': IPopulationPlugin,
            'base_plugin': BaseInterface,
        }

        # Everything is, at least, a base plugin.
        valid_types = set(['baseplugin'])
        # Loop through the types of plugins and check for implentation
        # of each.

        claimed_compliances = list(implementedBy(type(plugin)))
        # Can we use this as a map instead?
        for t, interface in plugin_types.iteritems():
            if interface in claimed_compliances:
                try:
                    verifyObject(interface, plugin)
                except DoesNotImplement:
                    log.error('Plugin %s claims to be a %s, but is not!',
                              plugin.name, t)
                else:
                    # If the above succeeded, then `plugin` implements
                    # `interface`.
                    insort(self.plugins[t], plugin)
                    valid_types.add(t)

        plugin.setup(self)

        log.info('registered plugin %s as %s', plugin.name, valid_types)

    def removePlugin(self, plugin):
        log.info("Unloading %r" % plugin)
        for plugin_type, plugins in self.plugins.items():
            if plugin in plugins:
                log.debug('plugin is a %s', plugin_type)
                plugins.remove(plugin)

    def runPlugins(self, category, func, protocol, *args):
        """
        Run the specified set of plugins against a given protocol.
        """

        stop = False

        # Plugins are already sorted by priority
        for plugin in self.plugins[category]:
            # If a plugin throws an exception, we should catch it gracefully.
            try:
                stop = getattr(plugin, func)(protocol, *args)
                if stop:
                    break
            except Exception:
                # A plugin should not be able to crash the bot.
                # Catch and log all errors.
                traceback.print_exc()
