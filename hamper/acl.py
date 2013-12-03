import json
import re


class AllowAllACL(object):
    def has_permission(self, comm, thing):
        return True


class ACL(object):

    ALLOW = 1
    DENY = 2

    def __init__(self, acl):
        self.acls = json.loads(acl)

    def has_permission(self, comm, thing):
        allow, deny = False, False
        self.add_groups(comm)

        for selector, permissions in self.acls.get('permissions', {}).items():
            if self.match_selector(selector, comm):
                for p in permissions:
                    policy = self.glob_permission_match(thing, p)
                    if policy == self.ALLOW:
                        allow = True
                    elif policy == self.DENY:
                        deny = True

        return allow and not deny

    def match_selector(self, selector, comm):
        parsed = self.parse_selector(selector)
        for key, val in parsed.items():
            if key == 'group':
                if val not in comm['groups']:
                    return False
            else:
                if comm[key] != val:
                    return False

        return True

    def parse_selector(self, selector):
        if selector == '*':
            return {}

        user = re.search(r'^([^@#]+)', selector)
        group = re.search(r'(@[^@#]+)', selector)
        channel = re.search(r'(#[^@#]+)', selector)

        parsed = {}
        if user:
            parsed['user'] = user.groups()[0]
        if group:
            parsed['group'] = group.groups()[0]
        if channel:
            parsed['channel'] = channel.groups()[0]

        return parsed

    def glob_permission_match(self, permission, pattern):
        if pattern[0] == '-':
            ret = self.DENY
            pattern = pattern[1:]
        else:
            ret = self.ALLOW

        permissions = permission.split('.')
        patterns = pattern.split('.')

        if len(permissions) != len(patterns) and patterns[-1] != '*':
            return False

        for perm, pat in zip(permissions, patterns):
            if perm != pat and pat != '*':
                return None
        return ret

    def add_groups(self, comm):
        user = comm.get('user')
        comm['groups'] = []
        for name, members in self.acls.get('groups', {}).items():
            if user in members:
                comm['groups'].append(name)
        # Yes it is modified, but returning it is nice too.
        return comm
