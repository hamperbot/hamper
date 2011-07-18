from datetime import datetime
import random

from zope.interface import implements
from sqlalchemy import Integer, String, Date, Column
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy

from hamper.plugins.commands import Plugin


class Quotes(Plugin):
    '''Remember quotes, and recall on demand.'''

    name = 'quotes'
    regex = r'^quote(.*)'

    def __init__(self):
        pass
        # TODO: make sure the tables we care about are in the db. how?


    def __call__(self, commander, opts):
        args = opts['groups'][0].strip()

        if args.startswith('--add '):
            # Add a quote
            text = args.split(' ', 1)[1]
            quote = Quote(text, opts['user'])
            commander.db.add(quote)
        else:
            # Deliver a quote
            index = random.randrange(0, commander.db.query(Quote).count())
            quote = commander.db.query(Quote)[rand]
            commander.say(quote.text)


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
