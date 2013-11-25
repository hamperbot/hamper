import json


class AllowAllACL(object):
    def hasPermission(self, comm, thing):
        return True


class ACL(object):
    def __init__(self, acl):
        self.acls = json.loads(acl)
        self.permissions = self.acls['permissions']

    def hasPermission(self, comm, thing):
        channel = comm['channel']

        # First, is this command allowed in this channel?
        if self.commandChannelPermission(channel, thing):
            return True
        return False

    def commandChannelPermission(self, channel, thing):
        channel_perms = self.permissions.get(channel, None)
        if channel_perms:
            if '-%s' % thing in channel_perms:
                return False
            if '*' in channel_perms:
                return True
            if thing in channel_perms:
                return True
        return False
