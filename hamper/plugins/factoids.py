import re
import random

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from hamper.interfaces import ChatPlugin
from hamper.utils import ude


SQLAlchemyBase = declarative_base()


class Factoids(ChatPlugin):
    """Learn and repeat Factoids."""
    name = 'factoids'
    priority = 2

    def setup(self, loader):
        super(Factoids, self).setup(loader)
        self.db = loader.db
        SQLAlchemyBase.metadata.create_all(self.db.engine)

        self.factoids = {}

    def message(self, bot, comm):
        subs = [self.try_add_factoid,
                self.try_forget_factoid,
                self.try_forget_factoid_mass,
                self.try_respond_to_factoid]

        ret = False
        for sub in subs:
            ret = sub(bot, comm)
            if ret:
                break
        return ret

    def try_add_factoid(self, bot, comm):
        if not comm['directed']:
            return

        msg = comm['message'].strip()
        match = re.match(r'learn(?: that)? (.+)\s+(\w+)\s+<(\w+)>\s+(.*)', msg)

        if not match:
            return

        if not bot.acl.has_permission(comm, 'factoid'):
            bot.reply(comm, "I cannot learn new things")
            return

        trigger, type_, action, response = match.groups()
        trigger = trigger.strip()

        if action not in ['say', 'reply', 'me']:
            bot.reply(comm, "I don't know the action {0}.".format(action))
            return
        if type_ not in ['is', 'triggers']:
            bot.reply(comm, "I don't the type {0}.".format(type_))
            return

        self.db.session.add(
            Factoid(ude(trigger), type_, action, ude(response))
        )
        self.db.session.commit()

        bot.reply(comm, 'OK, {user}'.format(**comm))

        return True

    def try_forget_factoid(self, bot, comm):
        if not comm['directed']:
            return

        msg = ude(comm['message'].strip())
        match = re.match(r'forget that\s+(.+)\s+is\s+(.*)', msg)

        if not match:
            return

        if not bot.acl.has_permission(comm, 'factoid'):
            bot.reply(comm, "Never Forget!")
            return

        trigger, response = match.groups()

        factoids = (self.db.session.query(Factoid)
                    .filter(Factoid.trigger == ude(trigger),
                            Factoid.response == ude(response))
                    .all())
        if len(factoids) == 0:
            bot.reply(comm, "I don't have anything like that.")
            return
        for factoid in factoids:
            self.db.session.delete(factoid)
        self.db.session.commit()
        bot.reply(comm, 'Done, {user}'.format(**comm))

        return True

    def try_forget_factoid_mass(self, bot, comm):
        if not comm['directed']:
            return

        msg = ude(comm['message'].strip())
        match = re.match(r'forget all about (.+)', msg)

        if not match:
            return

        if not bot.acl.has_permission(comm, 'factoid'):
            bot.reply(comm, "Never Forget!")
            return

        trigger = match.groups()[0]
        factoids = (self.db.session.query(Factoid)
                    .filter(Factoid.trigger == ude(trigger))
                    .all())

        if len(factoids) == 0:
            bot.reply(comm, "I don't have anything like that.")
            return

        for factoid in factoids:
            self.db.session.delete(factoid)
        self.db.session.commit()

        bot.reply(comm, 'Done, {user}'.format(**comm))

        return True

    def try_respond_to_factoid(self, bot, comm):
        msg = ude(comm['message'].strip())

        if comm['directed']:
            msg = '!' + msg

        factoids = (self.db.session.query(Factoid)
                    .filter(Factoid.trigger == msg)
                    .all())
        if len(factoids) == 0:
            factoids = (self.db.session.query(Factoid)
                        .filter(Factoid.type == 'triggers')
                        .all())
            factoids = filter(lambda f: f.trigger in msg, factoids)

        if len(factoids) == 0:
            return

        factoid = random.choice(factoids)
        if factoid.action == 'say':
            bot.reply(comm, factoid.response)
            return True
        elif factoid.action == 'reply':
            bot.reply(comm, '{}: {}'.format(comm['user'], factoid.response))
            return True
        elif factoid.action == 'me':
            bot.me(comm, factoid.response)
            return True
        else:
            bot.reply(comm, 'Um, what is the verb {}?'.format(factoid.action))


class Factoid(SQLAlchemyBase):
    '''The object that will get persisted by the database.'''

    __tablename__ = 'factoids'

    id = Column(Integer, primary_key=True)
    type = Column(String)
    trigger = Column(String)
    action = Column(String)
    response = Column(String)

    def __init__(self, trigger, type, action, response):
        self.type = type
        self.trigger = trigger
        self.action = action
        self.response = response
