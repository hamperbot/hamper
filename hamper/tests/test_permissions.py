import json
from unittest import TestCase

from hamper.acl import ACL

TEST_ACL = json.dumps({
    'groups': {
        '@ops': ['uberj', 'mythmon'],
        '@spammers': ['spambot'],
        '@7letters': ['mythmon', 'spambot'],
    },
    'permissions': {
        '#channel1': ['figlet', 'quote', '-quote.add'],
        '#channel2': ['*', '-figlet'],
        '@ops': ['*'],
        'mythmon': ['quote.*'],
    }
})


class TestACL(TestCase):
    def setUp(self):
        self.acl = ACL(TEST_ACL)

    def test_channel_star_perms(self):
        comm = {
            'user': 'uberj',
            'channel': '#channel2',
        }
        self.assertTrue(self.acl.has_permission(comm, 'foo'))

    def test_channel_perms(self):
        comm = {
            'user': 'foobar',
            'channel': '#channel1',
        }
        self.assertTrue(self.acl.has_permission(comm, 'figlet'))
        self.assertTrue(self.acl.has_permission(comm, 'quote'))
        self.assertFalse(self.acl.has_permission(comm, 'quote.add'))
        self.assertFalse(self.acl.has_permission(comm, 'channel.leave'))

    def test_channel_everything_but_figlet(self):
        comm = {
            'user': 'foobar',
            'channel': '#channel2',
        }
        self.assertTrue(self.acl.has_permission(comm, 'cmd'))
        self.assertTrue(self.acl.has_permission(comm, 'anothercmd'))
        self.assertFalse(self.acl.has_permission(comm, 'figlet'))

    def test_group_permissions(self):
        comm = {
            'user': 'uberj',
            'channel': '#channel3',
            # group will be filled in as '@op'
        }
        self.assertTrue(self.acl.has_permission(comm, 'cmd'))

        comm['channel'] = '#channel2'
        # Not even ops can use figlet here.
        self.assertFalse(self.acl.has_permission(comm, 'figlet'))

    def test_user_permission(self):
        comm = {
            'user': 'mythmon',
            'channel': '#channel3',
        }
        self.assertTrue(self.acl.has_permission(comm, 'quote'))
        self.assertTrue(self.acl.has_permission(comm, 'quote.add'))
        self.assertTrue(self.acl.has_permission(comm, 'quote.delete'))

    def test_empty_acls(self):
        # This should not error.
        acl = ACL('{}')
        acl.has_permission({}, 'foo')


class TestACLParser(TestCase):
    def setUp(self):
        self.acl = ACL(TEST_ACL)

    def _check(self, selector, expected):
        acl = ACL(TEST_ACL)
        self.assertEqual(acl.parse_selector(selector), expected)

    # 0 items

    def test_star(self):
        self._check('*', {})

    # 1 items

    def test_user(self):
        self._check('foo', {'user': 'foo'})
        self._check('bar', {'user': 'bar'})

    def test_group(self):
        self._check('@foo', {'group': '@foo'})
        self._check('@bar', {'group': '@bar'})

    def test_channel(self):
        self._check('#foo', {'channel': '#foo'})
        self._check('#bar', {'channel': '#bar'})

    # 2 items

    def test_user_group(self):
        self._check('foo@bar', {'user': 'foo', 'group': '@bar'})
        self._check('baz@qux', {'user': 'baz', 'group': '@qux'})

    def test_user_channel(self):
        self._check('foo#bar', {'user': 'foo', 'channel': '#bar'})
        self._check('baz#qux', {'user': 'baz', 'channel': '#qux'})

    def test_group_channel(self):
        self._check('@foo#bar', {'group': '@foo', 'channel': '#bar'})
        self._check('#baz@qux', {'channel': '#baz', 'group': '@qux'})

    # 3 items

    def test_user_channel_group(self):
        self._check('foo@bar#baz', {
            'user': 'foo',
            'group': '@bar',
            'channel': '#baz',
        })
        self._check('foo#baz@bar', {
            'user': 'foo',
            'group': '@bar',
            'channel': '#baz',
        })


class TestPermissionGlobbing(TestCase):

    def setUp(self):
        self.acl = ACL(TEST_ACL)

    def _check(self, perm, pattern, match=ACL.ALLOW):
        if match:
            self.assertTrue(self.acl.glob_permission_match(perm, pattern))
        else:
            self.assertFalse(self.acl.glob_permission_match(perm, pattern))

    def test_single(self):
        self._check('foo', 'foo')
        self._check('foo', 'bar', None)

    def test_dotted(self):
        self._check('foo.bar', 'foo.bar')
        self._check('foo.bar', 'foo.baz', None)

    def test_partial(self):
        self._check('foo', 'foo.bar', None)
        self._check('foo.bar', 'foo', None)

    def test_end_star(self):
        self._check('foo.bar', 'foo.*')
        self._check('foo.bar', 'bar.*', None)

    def test_middle_star(self):
        self._check('foo.bar.baz', 'foo.*.baz')
        self._check('foo.bar.baz', 'foo.*.qux', None)

    def test_partial_star(self):
        self._check('foo.bar.baz', 'foo.*')
        self._check('foo.bar.baz', 'bar.*', None)

    def test_negation(self):
        self._check('foo', '-foo', ACL.DENY)
        self._check('foo.bar', '-foo.bar', ACL.DENY)
        self._check('foo', '-foo.bar', None)


class TestAddGroups(TestCase):

    def setUp(self):
        self.acl = ACL(TEST_ACL)

    def test_single(self):
        comm = {'user': 'uberj'}
        self.assertEqual(self.acl.add_groups(comm)['groups'], ['@ops'])

    def test_double(self):
        comm = {'user': 'mythmon'}
        groups = set(self.acl.add_groups(comm)['groups'])
        expected = set(['@ops', '@7letters'])
        self.assertEqual(groups, expected)

    def test_none(self):
        comm = {'user': 'edunham'}
        self.assertEqual(self.acl.add_groups(comm)['groups'], [])
