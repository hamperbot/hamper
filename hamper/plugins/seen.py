from hamper.interfaces import (
    ChatCommandPlugin, Command, PopulationPlugin, PresencePlugin
)
from hamper.utils import ude

from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime

SQLAlchemyBase = declarative_base()


class Seen(ChatCommandPlugin, PopulationPlugin, PresencePlugin):
    """Keep track of when a user has last done something."""

    name = 'seen'
    priority = 10

    def setup(self, loader):
        super(Seen, self).setup(loader)
        self.db = loader.db
        SQLAlchemyBase.metadata.create_all(self.db.engine)

    def queryUser(self, channel, user):
        return (self.db.session.query(SeenTable)
                .filter(SeenTable.channel == channel)
                .filter(SeenTable.user == ude(user)))

    def record(self, channel, user, doing):
        logs = self.queryUser(channel, user)

        if logs.count():  # Because exists() doesn't exist?
            log = logs.first()
            log.seen = datetime.now()
            log.doing = ude(doing)
        else:
            self.db.session.add(
                SeenTable(channel, user, datetime.now(), ude(doing))
            )
        self.db.session.commit()

    def userJoined(self, bot, user, channel):
        self.record(channel, user, '(Joining)')
        return super(Seen, self).userJoined(bot, user, channel)

    def userLeft(self, bot, user, channel):
        self.record(channel, user, '(Leaving)')
        return super(Seen, self).userLeft(bot, user, channel)

    def message(self, bot, comm):
        self.record(comm['channel'], comm['user'], comm['raw_message'])
        return super(Seen, self).message(bot, comm)

    def userQuit(self, bot, user, quitMessage):
        # Go through every log we have for this user and set their most recent
        # doing to (Quiting with message 'quitMessage')
        logs = self.db.session.query(SeenTable).filter(
            SeenTable.user == ude(user)
        )
        logs.update({
            'doing': '(Quiting) with message "%s"' % ude(quitMessage),
            'seen': datetime.now()
        })
        return super(Seen, self).userQuit(bot, user, quitMessage)

    class SeenCommand(Command):
        """Say the last thing you've seen of a user"""
        regex = r'^seen (.*)$'

        name = 'seen'

        short_desc = 'seen <user> - When was the user last seen?'
        long_desc = ''

        def command(self, bot, comm, groups):
            if groups[0].isspace():
                return

            name = groups[0].strip()
            if name.lower() == bot.nickname.lower():
                bot.reply(comm, 'I am always here!')

            logs = self.plugin.queryUser(comm['channel'], name)

            if not logs.count():
                bot.reply(comm, 'I have not seen %s' % ude(name), encode=True)
            else:
                log = logs.first()
                time_format = 'at %I:%M %p on %b-%d'
                seen = log.seen.strftime(time_format)
                bot.reply(
                    comm, 'I observed %s %s -- %s' % (name, seen, log.doing)
                )


class SeenTable(SQLAlchemyBase):
    """One log per channel per user"""

    __tablename__ = 'seen'

    id = Column(Integer, primary_key=True)
    user = Column(String)
    channel = Column(String)
    seen = Column(DateTime)
    doing = Column(String)

    def __init__(self, channel, user, seen, doing):
        self.channel = channel
        self.user = user
        self.seen = seen
        self.doing = doing

    def __str__(self):
        return "%s %s %s %s" % (self.channel, self.user, self.seen, self.doing)

    def __repr__(self):
        return "<Seen %s>" % self
