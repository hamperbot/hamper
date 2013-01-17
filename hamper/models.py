from datetime import datetime


class User(object):

    def __init__(self, nickname, seen=datetime.now()):
        self.nickname = nickname
        # Default seen time is on creation.
        self.seen = seen

    def update_seen(self):
        self.seen = datetime.now()

    def __repr__(self):
        return self.nickname
