from datetime import datetime
import random

from zope.interface import implements
from sqlalchemy import Integer, String, Date, Column
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy

from hamper.interfaces import Command


class Quotes(Command):
    '''Remember quotes, and recall on demand.'''

    name = 'quotes'
    priority = 0
    regex = r'^quote(.*)$'

    def __init__(self):
        super(Quotes, self).__init__()
        # TODO: make sure the tables we care about are in the db. how?


    def command(self, bot, comm, groups):
        args = groups[0].strip()

        if args.startswith('--add '):
            # Add a quote
            text = args.split(' ', 1)[1]
            quote = Quote(text, opts['user'])
            bot.db.add(quote)
        else:
            # Deliver a quote
            index = random.randrange(0, bot.db.query(Quote).count())
            quote = bot.db.query(Quote)[rand]
            bot.say(quote.text)


Base = declarative_base()


class Quote(Base):
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
