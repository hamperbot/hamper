from datetime import datetime

from hamper.interfaces import (ChatCommandPlugin, Command, PopulationPlugin,
                               PresencePlugin)
from hamper.models import User


class Seen(ChatCommandPlugin, PopulationPlugin, PresencePlugin):
    """Keep track of when a user does something, and say when a user was last
    seen when asked"""

    name = 'seen'
    priority = 10
    users = {}

    @classmethod
    def update_users(cls, nickname):
        """Add or update an existing user in the users dict"""

        # get user if it exists
        user = cls.users.get(nickname, None)
        if user:
            cls.users[nickname].update_seen()
        else:
            # user doesnt exist, make object with current time as last seen
            # time.
            user = User(nickname, seen=datetime.now())
            # store the user object with the nickname for easy dict lookups
            user = {nickname: user}
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
        Seen.update_users(user)

    def userLeft(self, bot, user, channel):
        Seen.update_users(user)

    def userQuit(self, bot, user, quitMessage):
        Seen.update_users(user)

    def namesReply(self, bot, prefix, params):
        """called when the server replies to the NAMES request"""
        channel = params[2]
        nicks = params[3].split(' ')
        for nick in nicks:
            # Strip op status in name.
            if nick[0] in ['#', '@']:
                nick = nick[1:]
            Seen.update_users(nick)

    def namesEnd(self, bot, prefix, params):
        pass

    def message(self, bot, comm):
        nick = comm['user']
        Seen.update_users(nick)
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

            name = groups[0].strip().lower()
            user = self.plugin.users.get(name)
            if user == bot.nickname:
                bot.reply(comm, 'I am always here!')
            if user:
                bot.reply(comm, 'Seen {0.nickname} at {0.seen}'.format(user))
            else:
                bot.reply(comm, 'I have not seen {0}'.format(name))

    class NamesCommand(Command):
        """Say when you last saw a nickname"""
        regex = r'^(names?|users?|nicks?)\s?(?:list)?$'
        onlyDirected = False

        name = 'names'
        short_desc = 'Get the list of users in channel.'
        long_desc = None

        def command(self, bot, comm, groups):
            """Determine last time a nickname was seen"""
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

seen = Seen()
