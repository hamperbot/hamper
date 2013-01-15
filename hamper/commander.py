from collections import deque
import logging
import re
import traceback

from twisted.words.protocols import irc
from twisted.internet import protocol, reactor

from zope.interface.exceptions import DoesNotImplement

import sqlalchemy
from sqlalchemy import orm

from bravo.plugin import retrieve_named_plugins, verify_plugin, PluginException

import hamper.config
import hamper.log
from hamper.interfaces import IPlugin, IPresencePlugin, IChatPlugin, IPopulationPlugin


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
        return self.factory.db

    ##### Twisted events #####

    def signedOn(self):
        """Called after successfully signing on to the server."""
        log.info("Signed on as %s.", self.nickname)
        self.dispatch('presence', 'signedOn')
        for c in self.factory.channels:
            self.join(c)

    def joined(self, channel):
        """Called after successfully joining a channel."""
        print "Joined {0}.".format(channel)
        # ask for the current list of users in the channel
        self.names(channel)
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
            directed = target.lower() == self.nickname.lower()
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
        self.factory.db.commit()
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
        self.dispatch('population', 'userKicked', kickee, channel, kicker, message)

    def names(self, channel):
        """Sends the NAMES command to the IRC server."""
        channel = channel.lower()
        self.sendLine("NAMES %s" % channel)

    def irc_RPL_NAMREPLY(self, prefix, params):
        """Called when the server responds to my names request"""
        channel = params[2]
        nicks = params[3].split(' ')
        for nick in nicks:
            # Strip op status in name.
            if nick[0] in ['#', '@']:
                nick = nick[1:]
            self.factory.nicklist.add(nick)

    def irc_RPL_ENDOFNAMES(self, prefix, params):
        """Called after the names request is finished"""
        # print self.factory.nicklist
        pass

    ##### Hamper specific functions. #####

    def dispatch(self, category, func, *args):
        """Take a comm that has been parsed and dispatch it to plugins."""

        # Plugins are already sorted by priority
        stop = False
        for plugin in self.factory.plugins[category]:
            # If a plugin throws an exception, we should catch it gracefully.
            try:
                stop = getattr(plugin, func)(self, *args)
                if stop:
                    break
            except Exception:
                # A plugin should not be able to crash the bot.
                # Catch and log all errors.
                traceback.print_exc()

    def removePlugin(self, plugin):
        log.info("Unloading %r" % plugin)
        for plugin_type, plugins in self.factory.plugins.items():
            if plugin in plugins:
                log.debug('plugin is a %s', plugin_type)
                plugins.remove(plugin)

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
        self.config = config

        self.history = {}
        self.nicklist = set()
        self.plugins = {
            'base_plugin': [],
            'presence': [],
            'chat': [],
            'population': [],
        }

        if 'db' in config:
            print('Loading db from config: ' + config['db'])
            self.db_engine = sqlalchemy.create_engine(config['db'])
        else:
            print('Using in-memory db')
            self.db_engine = sqlalchemy.create_engine('sqlite:///:memory:')
        DBSession = orm.sessionmaker(self.db_engine)
        self.db = DBSession()

        # Load all plugins mentioned in the configuration. Allow globbing.
        plugins = retrieve_named_plugins(IPlugin, config['plugins'], 'hamper.plugins')
        for plugin in plugins:
            self.registerPlugin(plugin)

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s)." % (reason)

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason,)

    def registerPlugin(self, plugin):
        """Registers a plugin."""

        plugin_types = {
            'presence': IPresencePlugin,
            'chat': IChatPlugin,
            'population': IPopulationPlugin,
            'base_plugin': IPlugin,
        }

        # Everything is, at least, a base plugin.
        valid_types = ['baseplugin']
        # Loop through the types of plugins and check for implentation of each.
        for t, interface in plugin_types.iteritems():
            try:
                verified_plugin = verify_plugin(interface, plugin)
                # If the above succeeded, then `plugin` implementes `interface`.
                self.plugins[t].append(verified_plugin)
                self.plugins[t].sort()
                valid_types.append(t)
            except DoesNotImplement:
                # This means this plugin does not declare to  be a `t`.
                pass
            except PluginException:
                log.error('Plugin %s claims to be a %s, but is not!', plugin.name, t)

        plugin.setup(self)

        log.info('registered plugin %s as %s', plugin.name, valid_types)
