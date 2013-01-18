from datetime import datetime

from hamper.interfaces import (ChatCommandPlugin, Command, PopulationPlugin,
                               PresencePlugin)


class Seen(ChatCommandPlugin, PopulationPlugin, PresencePlugin):
    """Keep track of when a user does something, and say when a user was last
    seen when asked"""

    name = 'seen'
    priority = 10
    users = {}

    @classmethod
    def update_users(cls, bot, nickname, seen=True):
        """Add or update an existing user in the users dict"""

        # dont add the bot to the user dict
        if nickname == bot.nickname:
            return

        # get user if it exists
        user = cls.users.get(nickname, None)
        # only update seen if user exists, and seen is true
        if seen and user:
            cls.users[nickname].update_seen()
        else:
            # user doesn't exist.
            # if seen is true (default case for all but nameReply)
            # add them with current time as last seen
            if seen:
                user = User(nickname)
            else:
                # namesReply case, this is not a user action; so no seen time
                user = User(nickname, seen=None)

            # store the user object with the nickname for easy dict lookups
            user = {nickname.lower(): user}
            cls.users.update(user)

    @classmethod
    def names(cls, bot, channel):
        """Sends the NAMES command to the IRC server."""
        channel = channel.lower()
        bot.sendLine("NAMES %s" % channel)

    def joined(self, bot, channel):
        """called after the bot joins a channel"""
        # Send a names command
        Seen.names(bot, channel)

    def userJoined(self, bot, user, channel):
        """When user joins a channel, add them to the user dict"""
        Seen.update_users(bot, user)

    def userLeft(self, bot, user, channel):
        Seen.update_users(bot, user)

    def userQuit(self, bot, user, quitMessage):
        Seen.update_users(bot, user)

    def namesReply(self, bot, prefix, params):
        """called when the server replies to the NAMES request"""
        channel = params[2]
        nicks = params[3].split(' ')
        for nick in nicks:
            # Strip op status in name.
            if nick[0] in ['#', '@']:
                nick = nick[1:]
            Seen.update_users(bot, nick, seen=False)

    def namesEnd(self, bot, prefix, params):
        pass

    def message(self, bot, comm):
        nick = comm['user']
        Seen.update_users(bot, nick)
        # dispatch out to commands.
        return super(Seen, self).message(bot, comm)

    class SeenCommand(Command):
        """Say when you last saw a nickname"""
        regex = r'^seen (.*)$'
        onlyDirected = False

        name = 'seen'
        short_desc = 'seen username - When was user "username" last seen?'
        long_desc = None

        def command(self, bot, comm, groups):
            """Determine last time a nickname was seen"""
            if groups[0].isspace():
                return

            name = groups[0].strip()

            # Grab the user from the database
            user = self.plugin.users.get(name.lower(), None)
            if name.lower() == bot.nickname.lower():
                bot.reply(comm, 'I am always here!')
            # the user has never been seen
            elif user is None:
                bot.reply(comm, 'I have not seen {0}'.format(name))
            # user exists database and has been seen
            elif user.seen:
                time_format = 'at %I:%M %p on %b-%d'
                seen = user.seen.strftime(time_format)
                message = 'saying "%s"' % comm['message']
                bot.reply(comm, 'Seen {0.nickname} {1} {2}'
                          .format(user, seen, message))
            # if the user exists in the database, but has not been seen active
            # since the bot joined
            else:
                bot.reply(comm, 'I have not seen {0}'.format(name))

    class NamesCommand(Command):
        """List all users in the channel."""
        regex = r'^(names?|users?|nicks?)\s?(?:list)?$'
        onlyDirected = False

        name = 'names'
        short_desc = 'Get the list of users in channel.'
        long_desc = None

        def command(self, bot, comm, groups):
            """Print out a list of users in the channel"""
            # Could be better, anytime we're checking users we should send a
            # new names request, and set the command to be deffered until
            # namesEnd
            userlist = self.plugin.users
            nicknames = [nick for nick in userlist.keys()]
            if nicknames:
                message = ", ".join(nicknames)
                bot.reply(comm, '{0} list: {1}.'.format(groups[0], message))
            else:
                # Trigger a names request as a fall back.
                Seen.names()
                bot.reply(comm, 'No users in list. Needs work.')


class User(object):

    def __init__(self, nickname, seen=datetime.now()):
        self.nickname = nickname
        # Default seen time is on creation.
        self.seen = seen

    def update_seen(self):
        self.seen = datetime.now()

    def __repr__(self):
        return self.nickname


seen = Seen()
