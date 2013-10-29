import re

from hamper.interfaces import ChatCommandPlugin, Command

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

SQLAlchemyBase = declarative_base()


class Karma(ChatCommandPlugin):
    """
    Hamper will look for lines that end in ++ or -- and modify that user's 
    karma value accordingly

    There will also be !top5 and !bot5 to display those with the most and
    least karma

    NOTE: The user is just a string, this really could be anything...like
    potatoes or the infamous cookie clicker....
    """

    name = 'karma'

    def setup(self, loader):
        super(Karma, self).setup(loader)
        self.db = loader.db
        SQLAlchemyBase.metadata.create_all(self.db.engine)

    def message(self, bot, comm):
        """
        Check for strings ending with 2 or more '-' or '+'
        """

        super(Karma, self).message(bot, comm)
        msg = comm['message'].strip()

        add = re.search('\+\++$', msg)
        remove = re.search('--+$', msg)

        if add:
            self.add_karma(msg.rstrip('+'))
        elif remove:
            self.remove_karma(msg.rstrip('-'))

    def add_karma(self, user):
        """
        +1 Karma to a user
        """
        kt = self.db.session.query(KarmaTable)
        urow = kt.filter(KarmaTable.user==user).first()
        if not urow:
            urow = KarmaTable(user)
        urow.kcount += 1
        self.db.session.add(urow)
        self.db.session.commit()

    def remove_karma(self, user):
        """
        -1 Karma to a user
        """
        kt = self.db.session.query(KarmaTable)
        urow = kt.filter(KarmaTable.user==user).first()
        if not urow:
            urow = KarmaTable(user)
        urow.kcount -= 1
        self.db.session.add(urow)
        self.db.session.commit()


    class KarmaList(Command):
        """
        Return the top or bottom 5
        """

        regex = r'^karma --(top|bottom)$'

        LIST_MAX = 5

        def command(self, bot, comm, groups):
            users = bot.factory.loader.db.session.query(KarmaTable)
            user_count = users.count()
            top = self.LIST_MAX if user_count >= self.LIST_MAX else user_count

            if top:
                show = (KarmaTable.kcount.desc() if groups[0] == 'top'
                                                 else KarmaTable.kcount)
                for user in users.order_by(show)[0:top]:
                    bot.reply(comm, str('%s: %d' % (user.user, user.kcount)))
            else:
                bot.reply(comm, r'No one has any karma yet :-(')


class KarmaTable(SQLAlchemyBase):
    """
    Keep track of users karma in a persistant manner
    """

    __tablename__ = 'karma'

    # Calling the primary key user, though, really, this can be any string
    user = Column(String, primary_key=True)
    kcount = Column(Integer)


    def __init__(self, user, kcount=0):
        self.user = user
        self.kcount = kcount


karma = Karma()
