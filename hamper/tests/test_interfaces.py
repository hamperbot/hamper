from bisect import insort
from unittest import TestCase

from hamper.interfaces import ChatPlugin


class TestPlugin1(ChatPlugin):
    priority = 1


class TestPlugin2(ChatPlugin):
    priority = 2


class TestPlugin3(ChatPlugin):
    priority = 3


class TestPluginSorting(TestCase):

    def test_plugin_sorting(self):
        p1 = TestPlugin1()
        p2 = TestPlugin2()
        p3 = TestPlugin3()

        self.assertTrue(p1 < p3)
        self.assertTrue(p1 < p2)
        self.assertTrue(p2 < p3)
        self.assertTrue(p2 > p1)
        self.assertTrue(p3 > p1)
        self.assertTrue(p3 > p2)

    def test_plugin_insort(self):
        p1 = TestPlugin1()
        p2 = TestPlugin2()
        p3 = TestPlugin3()

        plugins = []
        insort(plugins, p1)
        insort(plugins, p3)
        insort(plugins, p2)
        self.assertEquals(plugins, [p1, p2, p3])

        plugins = []
        insort(plugins, p3)
        insort(plugins, p1)
        insort(plugins, p2)
        self.assertEquals(plugins, [p1, p2, p3])
