from unittest import TestCase

from hamper.interfaces import Command


class CommandSubclass(Command):
    regex = "^!test(.*)$"

    def command(self, unused, d, matches):
        self.matches = matches


class TestCommand(TestCase):
    """
    The Command class provides some basic structure for regex-powered
    commands.
    """

    def test_only_directed(self):
        c = CommandSubclass(None)

        d = {"directed": False}

        self.assertFalse(c.message(None, d))

    def test_no_match(self):
        c = CommandSubclass(None)
        c.onlyDirected = False

        d = {"directed": False, "message": "!example"}

        self.assertFalse(c.message(None, d))

    def test_simple_match(self):
        c = CommandSubclass(None)
        c.onlyDirected = False

        d = {"directed": False, "message": "!test"}

        self.assertTrue(c.message(None, d))
        self.assertEqual(c.matches, ("",))

    def test_match_groups(self):
        c = CommandSubclass(None)
        c.onlyDirected = False

        d = {"directed": False, "message": "!testing"}

        self.assertTrue(c.message(None, d))
        self.assertEqual(c.matches, ("ing",))
