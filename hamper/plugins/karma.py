import re

from hamper.interfaces import ChatCommandPlugin, Command

from sqlachemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

SQLALchemyBase = declarative_base()


class Karma(ChatCommandPlugin):
    """
    Hamper will look for lines that end in ++ or -- and modify that user's 
    karma value accordingly

    There will also be !top5 and !bot5 to display those with the most and
    least karma

    NOTE: The user is just a string, this really could be anything...like
    potatoes or the infamous cookie clicker....
    """

    def setup(self, loader):
        """
        """

        super(Karma, self).setup(loader)
        self.db = loader.db
        SQLAlchemyBase.metadata.create_all(self.db.engine)
        

    def message(self, bot, comm):
        """
        """

        super(Karma, self).message(bot, comm)
        msg = comm['message'].strip()

        add = re.match('\+\++$', msg)
        remove = re.match('--+$', msg)

        if add:
            self.add_karma(msg.rstrip('+'))
        elif remove:
            self.remove_karma(msg.rstrip('-'))



    def add_karma(self, user):
        """
        +1 Karma to a user
        """
        pass

    def remove_karma(self, user):
        """
        -1 Karma to a user
        """
        pass


    class Top(Command):
        pass


    class Bottom(Command):
        pass


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
