from unittest import TestCase

from hamper.plugins.factoids import FactoidsPlugin, Factoid
from hamper.tests import MockBot, make_comm


class TestFactoid(TestCase):

    def setUp(self):
        self.mock_bot = MockBot()
        self.plugin = FactoidsPlugin()
        self.plugin.setup(self.mock_bot)
        self.db_query = self.mock_bot.db.session.query
        self.session = self.mock_bot.db.session

    def tearDown(self):
        self.mock_bot.db.session.rollback()

    def test_noop(self):
        """Test that the bot does not respond when not intended."""
        comm = make_comm()
        self.plugin.message(self.mock_bot, comm)
        # No reply was sent.
        self.assertEqual(self.mock_bot.reply.call_count, 0)
        self.assertEqual(self.mock_bot.me.call_count, 0)

    def test_add(self):
        comm = make_comm(message='!learn that foo is <say> bar')
        self.plugin.message(self.mock_bot, comm)
        # Confirmation
        self.mock_bot.reply.assert_called_with(comm, 'OK, ' + comm['user'])
        # Exists in DB
        factoids = self.db_query(Factoid).all()
        self.assertEqual(len(factoids), 1)
        self.assertEqual(factoids[0].trigger, 'foo')
        self.assertEqual(factoids[0].type, 'is')
        self.assertEqual(factoids[0].action, 'say')
        self.assertEqual(factoids[0].response, 'bar')

    def test_remove_success(self):
        f = Factoid(type='is', trigger='foo', action='say', response='bar')
        self.session.add(f)
        self.session.flush()
        comm = make_comm(
            message='!forget that {0.trigger} is {0.response}'.format(f))
        self.assertEqual(self.db_query(Factoid).count(), 1)
        self.plugin.message(self.mock_bot, comm)
        self.assertEqual(self.db_query(Factoid).count(), 0)

    def test_remove_missing(self):
        comm = make_comm(message='!forget that foo is bar')
        self.plugin.message(self.mock_bot, comm)
        self.mock_bot.reply.assert_called_with(
            comm, "I don't have anything like that.")
