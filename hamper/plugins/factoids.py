import random
from collections import namedtuple

# from sqlalchemy import Column, Integer, String
# from sqlalchemy.ext.declarative import declarative_base

from hamper.interfaces import ChatCommandPlugin, Command
# from hamper.utils import ude


# SQLAlchemyBase = declarative_base()


class FactoidsPlugin(ChatCommandPlugin):
    """Learn and repeat Factoids."""
    name = 'factoids'
    priority = 2

    def setup(self, loader):
        super(FactoidsPlugin, self).setup(loader)
        # self.db = loader.db
        # SQLAlchemyBase.metadata.create_all(self.db.engine)

        self.factoids = []

    def message(self, bot, comm):
        ret = super(FactoidsPlugin, self).message(bot, comm)
        if ret:
            return ret

        msg = comm['message']
        choices = []
        for f in self.factoids:
            if f.type == 'triggers' and f.trigger in msg:
                choices.append(f)
            elif f.type == 'is' and f.trigger == msg:
                choices.append(f)
        if choices:
            choice = random.choice(choices)
            if choice.action == 'say':
                bot.reply(comm, choice.response)
            elif choice.action == 'reply':
                bot.reply(comm, '{}: {}'.format(comm['user'], choice.response))
            elif choice.action == 'me':
                bot.me(comm, choice.response)

            return True

        return False

    class AddFactoid(Command):

        name = 'add'
        regex = r'learn(?: that)?\s+(.+)\s+(\w+)\s+<(\w+)>\s+(.*)'

        def command(self, bot, comm, groups):
            if not bot.acl.has_permission(comm, 'factoid.add'):
                bot.reply(comm, 'You cannot teach me new things.')
                return

            trigger, type_, action, response = groups

            if action not in ['say', 'reply', 'me']:
                bot.reply(comm, "I don't know the action '{}'.".format(action))
                return

            if type_ not in ['is', 'triggers']:
                bot.reply(comm, "I don't know the type '{}'.".format(type_))
                return

            self.plugin.factoids.append(Factoid(trigger, type_, action,
                                                response))
            bot.reply(comm, 'OK, {}'.format(comm['user']))
            return True

    class RemoveFactoid(Command):

        name = 'remove'
        regex = r'forget that\s+(.+)\s+is\s+(.+)'

        def command(self, bot, comm, groups):
            if not bot.acl.has_permission(comm, 'factoid.remove'):
                bot.reply(comm, 'Never forget!')
                return

            trigger, response = groups

            len_before = len(self.plugin.factoids)
            self.plugin.factoids = [f for f in self.plugin.factoids
                                    if f.trigger != trigger
                                    or f.response != response]
            len_after = len(self.plugin.factoids)

            if len_after < len_before:
                bot.reply(comm, 'Done, {}.'.format(comm['user']))
                return True
            else:
                bot.reply(comm, "I don't have anything like that.")

    class MassRemoveFactoid(Command):

        name = 'massremove'
        regex = r'forget all about\s+(.+)'

        def command(self, bot, comm, groups):
            if not bot.acl.has_permission(comm, 'factoid.massremove'):
                bot.reply(comm, 'Never forget!')
                return

            trigger = groups[0]

            len_before = len(self.plugin.factoids)
            self.plugin.factoids = [f for f in self.plugin.factoids
                                    if f.trigger != trigger]
            len_after = len(self.plugin.factoids)

            if len_after < len_before:
                bot.reply(comm, 'Done, {}.'.format(comm['user']))
                return True
            else:
                bot.reply(comm, "I don't have anything like that.")


Factoid = namedtuple('Factoid', ['trigger', 'type', 'action', 'response'])


factoids = FactoidsPlugin()
