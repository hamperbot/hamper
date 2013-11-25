try:
    import StringIO
except ImportError:
    from io import StringIO  # Python 3

from unittest import TestCase

from hamper.acl import ACL

TEST_ACL = """
{
    "permissions": {
        "#channel": [
            "*"
        ],
        "#channel1": [
            "figlet",
            "quote",
            "-quote.add"
        ],
        "#channel2": [
            "*",
            "-figlet"
        ]
    }
}
"""


class TestACL(TestCase):
    def test_channel_star_perms(self):
        acl = ACL(StringIO.StringIO(TEST_ACL.strip('\n')).read())
        comm = {
            'user': 'uberj',
            'channel': '#channel',
        }
        self.assertTrue(acl.hasPermission(comm, 'foo'))

    def test_channel_perms(self):
        acl = ACL(StringIO.StringIO(TEST_ACL).read())
        comm = {
            'user': 'foobar',  # not in any groups
            'channel': '#channel1',
        }
        self.assertTrue(acl.hasPermission(comm, 'figlet'))
        self.assertTrue(acl.hasPermission(comm, 'quote'))
        self.assertFalse(acl.hasPermission(comm, 'quote.add'))
        self.assertFalse(acl.hasPermission(comm, 'channel.leave'))

    def test_channel_everything_but_figlet(self):
        acl = ACL(StringIO.StringIO(TEST_ACL).read())
        comm = {
            'user': 'foobar',  # not in any groups
            'channel': '#channel2',
        }
        self.assertTrue(acl.hasPermission(comm, 'cmd'))
        self.assertTrue(acl.hasPermission(comm, 'anothercmd'))
        self.assertFalse(acl.hasPermission(comm, 'figlet'))
