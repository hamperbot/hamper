from datetime import datetime
import random

from zope.interface import implements
from sqlalchemy import Integer, String, Date, Column
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy

from hamper.interfaces import Command, Plugin


SQLAlchemyBase = declarative_base()


class Quotes(Plugin):
    '''Remember quotes, and recall on demand.'''

    name = 'quotes'
    priority = 0

    def setup(self, factory):
        SQLAlchemyBase.metadata.create_all(factory.db_engine)

    class DeliverQuote(Command):
        """Deliver a quote."""
        regex = r'^quotes?$'
        def command(self, bot, comm, groups):
            index = random.randrange(0, bot.db.query(Quote).count() + 1)
            quote = bot.factory.db.query(Quote)[index]
            # Lame twisted irc doesn't support unicode.
            bot.msg(comm['channel'], str(quote.text))
            return True

    class AddQuote(Command):
        """Add a quote."""
        regex = r'^quotes? --add (.*)$'
        def command(self, bot, comm, groups):
            text = ' '.join(groups[0])
            quote = Quote(text, comm['user'])
            bot.factory.db.add(quote)
            bot.msg(comm['channel'], 'Succesfully added quote.')

    class CountQuotes(Command):
        """Count how many quotes the bot knows."""
        regex = r'^quotes? --count$'
        def command(self, bot, comm, groups):
            count = bot.db.query(Quote).count()
            bot.msg(comm['channel'], 'I know {0} quotes.'.format(count))


class Quote(SQLAlchemyBase):
    '''The object that will get persisted by the database.'''

    __tablename__ = 'quotes'

    id = Column(Integer, primary_key=True)
    text = Column(String)
    adder = Column(String)
    added = Column(Date)

    def __init__(self, text, adder, added=None):
        if not added:
            added = datetime.now()

        self.text = text
        self.adder = adder
        self.added = added


quotes = Quotes()
