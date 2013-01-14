from datetime import datetime

from hamper.interfaces import Command, ChatCommandPlugin, PopulationPlugin
from hamper.models import User


class Seen(ChatCommandPlugin):
    """Keep track of when a user does something, and say when a user was last
    seen when asked"""

    name = 'seen'
    priority = 10
    users = {}

    def message(self, bot, comm):
        nick = comm['user']
        for nickname in bot.factory.nicklist:
            if nickname == nick:
                # create user object with seen time for users list.
                user = User(nickname, seen=datetime.now())
                # store the user object with the nickname for easy lookup
                user = {nickname: user}
                self.users.update(user)
                break
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
            userlist = self.plugin.users
            name = groups[0]
            if name == bot.nickname:
                bot.reply(comm, 'I am always here!')
                return
            try:
                user = userlist[name]
                bot.reply(comm, 'Seen {0.nickname} at {0.seen}'.format(user))
            except KeyError:
                bot.reply(comm, 'I have not seen {0}'.format(name))

seen = Seen()
