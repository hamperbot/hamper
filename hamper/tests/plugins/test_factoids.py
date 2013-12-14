import random
from unittest import TestCase

from hamper.plugins.factoids import FactoidsPlugin, Factoid
from hamper.tests import MockBot, make_comm


class TestFactoid(TestCase):

    def factoid(self, **kwargs):
        words = ['apple', 'banana', 'cherry', 'date', 'eggplant', 'fig']
        data = {
            'trigger': ' '.join(random.choice(words) for _ in range(4)),
            'type': 'is',
            'action': 'say',
            'response': ' '.join(random.choice(words) for _ in range(4)),
        }
        data.update(kwargs)

        f = Factoid(**data)
        self.plugin.factoids.append(f)
        return f

    def setUp(self):
        self.mock_bot = MockBot()
        self.plugin = FactoidsPlugin()
        self.plugin.setup(self.mock_bot)
        self.session = self.mock_bot.db.session

    def tearDown(self):
        self.mock_bot.db.session.rollback()

    def test_noop(self):
        """Test that the bot does not respond when not intended."""
        self.mock_bot.reply.side_effect = AssertionError
        self.mock_bot.me.side_effect = AssertionError
        comm = make_comm()
        self.plugin.message(self.mock_bot, comm)

    def test_add(self):
        comm = make_comm(message='!learn that foo is <say> bar')
        self.plugin.message(self.mock_bot, comm)
        # Confirmation
        self.mock_bot.reply.assert_called_with(comm, 'OK, ' + comm['user'])
        # Exists in DB
        factoids = self.plugin.factoids
        self.assertEqual(len(factoids), 1)
        self.assertEqual(factoids[0].trigger, 'foo')
        self.assertEqual(factoids[0].type, 'is')
        self.assertEqual(factoids[0].action, 'say')
        self.assertEqual(factoids[0].response, 'bar')

    def test_remove_success(self):
        f = self.factoid()
        comm = make_comm(message='!forget that {0.trigger} is {0.response}'
                         .format(f))
        self.plugin.message(self.mock_bot, comm)
        self.assertEqual(len(self.plugin.factoids), 0)

    def test_remove_missing(self):
        comm = make_comm(message='!forget that foo is bar')
        self.plugin.message(self.mock_bot, comm)
        self.mock_bot.reply.assert_called_with(
            comm, "I don't have anything like that.")

    def test_remove_mass(self):
        for response in ['bar', 'baz', 'qux']:
            self.factoid(trigger='foo', response=response)
        comm = make_comm(message='!forget all about foo')
        self.plugin.message(self.mock_bot, comm)
        self.assertEqual(len(self.plugin.factoids), 0)

    def test_response_say(self):
        f = self.factoid(action='say')
        comm = make_comm(message=f.trigger)
        self.plugin.message(self.mock_bot, comm)
        self.mock_bot.reply.assert_called_with(comm, f.response)

    def test_response_reply(self):
        f = self.factoid(action='reply')
        comm = make_comm(user='bob', message=f.trigger)
        self.plugin.message(self.mock_bot, comm)
        self.mock_bot.reply.assert_called_with(comm, 'bob: ' + f.response)

    def test_response_me(self):
        f = self.factoid(action='me')
        comm = make_comm(user='bob', message=f.trigger)
        self.plugin.message(self.mock_bot, comm)
        self.mock_bot.me.assert_called_with(comm, f.response)

    def test_response_no_triggers(self):
        self.mock_bot.reply.side_effect = AssertionError
        self.mock_bot.me.side_effect = AssertionError
        f = self.factoid()
        comm = make_comm(message=f.trigger + ' something else')
        self.plugin.message(self.mock_bot, comm)

    def test_response_triggers(self):
        f = self.factoid(type='triggers')
        comm = make_comm(message=f.trigger + ' something else')
        self.plugin.message(self.mock_bot, comm)
        self.mock_bot.reply.assert_called_with(comm, f.response)
