import re
import random

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from hamper.interfaces import ChatPlugin

import q


SQLAlchemyBase = declarative_base()


class Factoids(ChatPlugin):
    """Learn and repeat Factoids."""
    name = 'factoids'
    priority = -1

    def setup(self, loader):
        super(Factoids, self).setup(loader)
        self.db = loader.db
        SQLAlchemyBase.metadata.create_all(self.db.engine)

        self.factoids = {}

    def message(self, bot, comm):
        ret = self.try_add_factoid(bot, comm)
        if ret:
            return True
        return self.try_respond_to_factoid(bot, comm)

    def try_add_factoid(self, bot, comm):
        if not comm['directed']:
            return

        msg = comm['message'].strip()
        match = re.match(r'(.*)\s+is\s+<(\w+)>\s+(.*)', msg)

        if not match:
            return

        trigger, action, response = match.groups()

        if action not in ['say', 'reply', 'me']:
            bot.reply(comm, "I don't know the action {0}.".format(action))
            return

        q(trigger, action, response)
        self.db.session.add(Factoid(trigger, action, response))
        self.db.session.commit()
        bot.reply(comm, 'OK, {user}'.format(**comm))

        return True

    def try_respond_to_factoid(self, bot, comm):
        msg = comm['message'].strip()

        factoids = (self.db.session.query(Factoid)
                    .filter(Factoid.trigger == msg)
                    .all())
        if len(factoids) == 0:
            return

        q(factoids)

        factoid = random.choice(factoids)

        if factoid.action == 'say':
            bot.reply(comm, factoid.response)
        elif factoid.action == 'reply':
            bot.reply(comm, '{}: {}'.format(comm['user'], factoid.response))
        else:
            bot.reply(comm, 'Um, what is the verb {}?'.format(factoid.action))


class Factoid(SQLAlchemyBase):
    '''The object that will get persisted by the database.'''

    __tablename__ = 'factoids'

    id = Column(Integer, primary_key=True)
    trigger = Column(String)
    action = Column(String)
    response = Column(String)

    def __init__(self, trigger, action, response):
        self.trigger = trigger
        self.action = action
        self.response = response


factoids = Factoids()
