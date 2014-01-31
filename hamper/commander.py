import importlib
import logging
import re
import traceback
from bisect import insort
from collections import deque, namedtuple
from fnmatch import fnmatch

from twisted.words.protocols import irc
from twisted.internet import protocol, reactor, ssl
from twisted.plugin import getPlugins
from zope.interface import implementedBy
from zope.interface.verify import verifyObject
from zope.interface.exceptions import DoesNotImplement

import sqlalchemy
from sqlalchemy import orm

import hamper.config
import hamper.log
import hamper.plugins
from hamper.acl import ACL, AllowAllACL
from hamper.interfaces import (BaseInterface, IPresencePlugin, IChatPlugin,
                               IPopulationPlugin)

log = logging.getLogger('hamper')


def main():
    config = hamper.config.load()
    hamper.log.setup_logging()

    if config.get('ssl', False):
        reactor.connectSSL(
            config['server'], config['port'], CommanderFactory(config),
            ssl.ClientContextFactory())
    else:
        reactor.connectTCP(
            config['server'], config['port'], CommanderFactory(config))
    reactor.run()


class CommanderProtocol(irc.IRCClient):
    """Interacts with a single server, and delegates to the plugins."""

    ##### Properties #####
    @property
    def nickname(self):
        return self.factory.nickname

    @property
    def password(self):
        return self.factory.password

    @property
    def db(self):
        return self.factory.loader.db

    @property
    def acl(self):
        return self.factory.acl

    ##### Twisted events #####

    def signedOn(self):
        """Called after successfully signing on to the server."""
        log.info("Signed on as %s.", self.nickname)
        if not self.password:
            # We aren't wating for auth, join all the channels
            self.joinChannels()
        else:
            self.msg("NickServ", "IDENTIFY %s" % self.password)

    def joinChannels(self):
        self.dispatch('presence', 'signedOn')
        for c in self.factory.channels:
            self.join(*c)

    def joined(self, channel):
        """Called after successfully joining a channel."""
        log.info("Joined {0}.".format(channel))
        # ask for the current list of users in the channel
        self.dispatch('presence', 'joined', channel)

    def left(self, channel):
        """Called after leaving a channel."""
        log.info("Left {0}.".format(channel))
        self.dispatch('presence', 'left', channel)

    def privmsg(self, raw_user, channel, raw_message):
        """Called when a message is received from a channel or user."""
        log.info(channel, raw_user, raw_message)

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

    def noticed(self, user, channel, message):
        log.info("NOTICE %s %s %s" % (user, channel, message))
        # mozilla's nickserv responds as NickServ!services@mozilla.org
        if (self.password and channel == self.nickname and
                user.startswith('NickServ')):
            if ("Password accepted" in message or
                    "You are now identified" in message):
                self.joinChannels()
            elif "Password incorrect" in message:
                log.info("NickServ AUTH FAILED!!!!!!!")
                reactor.stop()

    ##### Hamper specific functions. #####

    def dispatch(self, category, func, *args):
        """Take a comm that has been parsed and dispatch it to plugins."""

        self.factory.loader.runPlugins(category, func, self, *args)

    def reply(self, comm, message, encode=True):
        if encode:
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
        self.password = config.get('password', None)
        self.history = {}
        acl_fname = config.get('acl', None)

        if acl_fname:
            # Bubble up an IOError if they passed a bad file
            with open(acl_fname, 'r') as acl_fd:
                self.acl = ACL(acl_fd.read())
        else:
            self.acl = AllowAllACL()

        self.loader = PluginLoader(config)

        if 'db' in config:
            log.info('Loading db from config: ' + config['db'])
            db_engine = sqlalchemy.create_engine(config['db'])
        else:
            log.info('Using in-memory db')
            db_engine = sqlalchemy.create_engine('sqlite:///:memory:')

        DBSession = orm.sessionmaker(db_engine)
        session = DBSession()
        self.loader.db = DB(db_engine, session)

        self.loader.loadAll()

    def clientConnectionLost(self, connector, reason):
        log.info("Lost connection (%s)." % (reason))
        # Reconnect
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        log.info("Could not connect: %s" % (reason,))


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

    def __init__(self, config):
        self.config = config
        self.plugins = {
            'base_plugin': [],
            'presence': [],
            'chat': [],
            'population': [],
        }

    def loadAll(self):
        """
        Find and load all plugins mentioned in config['plugins'].

        This will allow for globbing and external plugins. To load an
        external plugin, give an import path like

            base/plugin

        where base is a import path to a package, and plugin is the name
        of a plugin that can be found *in one of that package's modules.*

        In other words, if you have a package foo, and in that package
        a module bar, and in that module a plugin named baz, listing
        'foo/bar/baz' *WILL NOT WORK*.

        Instead, list 'foo/baz', since the importer will look for a
        module that contains a plugin name 'baz' in the package 'foo'.
        Twisted's plugin loader is weird.

        For confusion's sake, I recommend naming modules in packages
        after the plugin they contain. So in the last example, either
        rename the plugin to bar or rename the module to baz.
        """
        modules = [('', hamper.plugins)]
        for spec in self.config['plugins']:
            # if this is not a qualified name, `hamper.plugins` will cover it.
            if '/' not in spec:
                continue
            # Given something with some dots, get everything up to but
            # excluding the last dot.
            index = spec.rindex('/')
            base = spec[:index].replace('/', '.')

            modules.append((base + '/', importlib.import_module(base)))

        config_matches = set()
        for base, module in modules:
            for plugin in getPlugins(BaseInterface, module):
                for pattern in self.config['plugins']:
                    full_name = base + plugin.name
                    if fnmatch(full_name, pattern):
                        self.registerPlugin(plugin)
                        config_matches.add(pattern)
                        break

        for pattern in self.config['plugins']:
            if pattern not in config_matches:
                log.warning('No plugin loaded for "{0}"'.format(pattern))

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
