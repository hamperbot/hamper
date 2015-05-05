import logging
import re
import traceback
from collections import deque, namedtuple

from twisted.words.protocols import irc
from twisted.internet import protocol, reactor, ssl
from pkg_resources import iter_entry_points

import sqlalchemy
from sqlalchemy import orm

import hamper.config
import hamper.log
import hamper.plugins
from hamper.acl import ACL, AllowAllACL

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
        log.info("Joined %s.", channel)
        # ask for the current list of users in the channel
        self.dispatch('presence', 'joined', channel)

    def left(self, channel):
        """Called after leaving a channel."""
        log.info("Left %s.", channel)
        self.dispatch('presence', 'left', channel)

    def action(self, raw_user, channel, raw_message):
        return self.process_action(raw_user, channel, raw_message)

    def privmsg(self, raw_user, channel, raw_message):
        return self.process_action(raw_user, channel, raw_message)

    def process_action(self, raw_user, channel, raw_message):
        """Called when a message is received from a channel or user."""
        log.info("%s %s %s", channel, raw_user, raw_message)

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

        if directed:
            message = message.rstrip()

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

        self.factory.history.setdefault(channel, deque(maxlen=100)).append(comm)

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
        """Dispatch an event to all listening plugins."""
        self.factory.loader.runPlugins(category, func, self, *args)

    def _hamper_send(self, func, comm, message, encode, tag, vars, kwvars):
        if type(message) == str:
            log.warning('Warning, passing message as ascii instead of unicode '
                        'will cause problems. The message is: {0}'
                        .format(message))

        format_kwargs = {}
        format_kwargs.update(kwvars)
        format_kwargs.update(comm)
        try:
            message = message.format(*vars, **format_kwargs)
        except (ValueError, KeyError, IndexError) as e:
            log.error('Could not format message: {e}'.format(e=e))

        if encode:
            message = message.encode('utf8')

        if comm['pm']:
            func(comm['user'], message)
        else:
            func(comm['channel'], message)

        (self.factory.sent_messages
            .setdefault(comm['channel'], deque(maxlen=100))
            .append({
                'comm': comm,
                'message': message,
                'tag': tag,
            }))


    def reply(self, comm, message, encode=True, tag=None, vars=[], kwvars={}):
        self._hamper_send(self.msg, comm, message, encode, tag, vars, kwvars)

    def me(self, comm, message, encode=True, tag=None, vars=[], kwvars={}):
        self._hamper_send(self.describe, comm, message, encode, tag, vars, kwvars)



class CommanderFactory(protocol.ClientFactory):
    protocol = CommanderProtocol

    def __init__(self, config):
        self.channels = [c.split(' ', 1) for c in config['channels']]
        self.nickname = config['nickname']
        self.password = config.get('password', None)
        self.history = {}
        self.sent_messages = {}
        acl_fname = config.get('acl', None)

        if acl_fname:
            # Bubble up an IOError if they passed a bad file
            with open(acl_fname, 'r') as acl_fd:
                self.acl = ACL(acl_fd.read())
            log.info('Loaded ACLs from %s', acl_fname)
        else:
            self.acl = AllowAllACL()
            log.info('Using no-op ACLs.')

        self.loader = PluginLoader(config)

        if 'db' in config:
            log.info('Loading db from config: %s', config['db'])
            db_engine = sqlalchemy.create_engine(config['db'])
        else:
            log.info('Using in-memory db')
            db_engine = sqlalchemy.create_engine('sqlite:///:memory:')

        DBSession = orm.sessionmaker(db_engine)
        session = DBSession()
        self.loader.db = DB(db_engine, session)

        self.loader.loadAll()

    def clientConnectionLost(self, connector, reason):
        log.info('Lost connection (%s).', (reason))
        # Reconnect
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        log.info('Could not connect: %s', (reason,))


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
        self.plugins = []


    def loadAll(self):
        plugins_to_load = set()

        # Gather plugins
        for plugin in iter_entry_points(group='hamperbot.plugins', name=None):
            if plugin.name in self.config['plugins']:
                plugins_to_load.add(plugin.load())

        # Sort by priority, highest first
        plugins_to_load = sorted(plugins_to_load, key=lambda p: -p.priority)

        # Check dependencies and load plugins.
        for plugin_class in plugins_to_load:
            plugin_obj = plugin_class()
            if not self.dependencies_satisfied(plugin_obj):
                log.warning('Dependency not satisfied for {0}. Not loading.'
                            .format(plugin_class.__name__))
                continue
            log.info('Loading plugin {0}.'.format(plugin_class.__name__))
            plugin_obj.setup(self)
            self.plugins.append(plugin_obj)

        # Check for missing plugins
        plugin_names = {x.name for x in self.plugins}
        for pattern in self.config['plugins']:
            if pattern not in plugin_names:
                log.warning('Sorry, I couldn\'t find a plugin named "%s"',
                            pattern)

    def dependencies_satisfied(self, plugin):
        """
        Checks whether a plugin's dependencies are satisfied.

        Logs an error if there is an unsatisfied dependencies
        Returns: Bool
        """
        for depends in plugin.dependencies:
            if depends not in self.config['plugins']:
                log.error("{0} depends on {1}, but {1} wasn't in the "
                          "config file. To use {0}, install {1} and add "
                          "it to the config.".format(plugin.name, depends))
                return False
        return True

    def runPlugins(self, category, func, protocol, *args):
        """
        Run the specified set of plugins against a given protocol.
        """
        # Plugins are already sorted by priority
        for plugin in self.plugins:
            # If a plugin throws an exception, we should catch it gracefully.
            try:
                event_listener = getattr(plugin, func)
            except AttributeError:
                # If the plugin doesn't implement the event, do nothing
                pass
            else:
                try:
                    stop = event_listener(protocol, *args)
                    if stop:
                        break
                except Exception:
                    # A plugin should not be able to crash the bot.
                    # Catch and log all errors.
                    traceback.print_exc()
