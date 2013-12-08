import sqlalchemy
from mock import MagicMock
from zope.interface import implements

from hamper.interfaces import ICommander
from hamper.commander import DB


class MockBot(MagicMock):
    implements(ICommander)

    def __init__(self, *args, **kwargs):
        super(MockBot, self).__init__(*args, **kwargs)

        db_engine = sqlalchemy.create_engine('sqlite:///:memory:')
        session = sqlalchemy.orm.sessionmaker(
            bind=db_engine,
            autocommit=False,
            autoflush=False)()
        self.db = DB(db_engine, session)


def make_comm(**kwargs):
    comm = {
        'user': 'bob',
        'channel': '#coolplace',
        'message': 'oh hai',
        'pm': False,
    }
    comm.update(kwargs)

    if comm['message'][0] == '!':
        comm['directed'] = True
        comm['message'] = comm['message'][1:]
    else:
        comm['directed'] = False

    return comm
