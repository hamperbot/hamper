from datetime import datetime
import random

from sqlalchemy import Integer, String, Date, Column
from sqlalchemy.ext.declarative import declarative_base

from hamper.interfaces import Command, ChatCommandPlugin
from hamper.utils import uen


SQLAlchemyBase = declarative_base()


class Quotes(ChatCommandPlugin):
    '''Remember quotes, and recall on demand.'''

    name = 'quotes'
    priority = 0

    def setup(self, loader):
        super(Quotes, self).setup(loader)
        SQLAlchemyBase.metadata.create_all(loader.db.engine)

    class DeliverQuote(Command):
        """Deliver a quote."""
        regex = r'^quotes?$'

        name = 'quote'
        short_desc = 'quote - Show, add, or count quotes.'
        long_desc = ('quote - Show a quote\n'
                     'quote --add QUOTE - Add a quote\n'
                     'quote --count - Count quotes\n')

        def command(self, bot, comm, groups):
            index = random.randrange(0, bot.db.session.query(Quote).count())
            quote = bot.factory.loader.db.session.query(Quote)[index]
            bot.reply(comm, uen(quote.text))
            return True

    class AddQuote(Command):
        """Add a quote."""
        regex = r'^quotes? --add (.*)$'

        def command(self, bot, comm, groups):
            text = groups[0]
            quote = Quote(text, comm['user'])
            bot.factory.loader.db.session.add(quote)
            bot.reply(comm, 'Successfully added quote.')

    class CountQuotes(Command):
        """Count how many quotes the bot knows."""
        regex = r'^quotes? --count$'

        def command(self, bot, comm, groups):
            count = bot.factory.loader.db.session.query(Quote).count()
            bot.reply(comm, 'I know {0} quotes.'.format(count))


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
