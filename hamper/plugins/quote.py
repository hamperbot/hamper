from datetime import datetime
import random

from zope.interface import implements
from sqlalchemy import Integer, String, Date, Column
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy

from hamper.interfaces import Command


SQLAlchemyBase = declarative_base()

class Quotes(Command):
    '''Remember quotes, and recall on demand.'''

    name = 'quotes'
    priority = 0
    regex = r'^quotes?(?: +(.*))?$'

    def setup(self, factory):
        SQLAlchemyBase.metadata.create_all(factory.db_engine)

    def command(self, bot, comm, groups):
        if groups[0]:
            args = groups[0].strip()
        else:
            args = ''

        if args.startswith('--add'):
            # Add a quote
            text = args.split(' ', 1)[1]
            print('trying to add quote: "{}".'.format(text))
            quote = Quote(text, comm['user'])
            bot.factory.db.add(quote)
            bot.say('Succesfully added quote.')
        else:
            # Deliver a quote
            print('trying to repeat a quote')
            index = random.randrange(0, bot.db.query(Quote).count())
            quote = bot.factory.db.query(Quote)[index]
            # Lame twisted irc doesn't support unicode.
            bot.say(str(quote.text))


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
