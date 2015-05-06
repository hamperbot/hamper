from twisted.internet import reactor
from twisted.internet.stdio import StandardIO
from twisted.protocols.basic import LineReceiver

import sqlalchemy
from sqlalchemy import orm

from hamper.commander import DB, PluginLoader
import hamper.config
import hamper.log


class CLIProtocol(LineReceiver):
    """
    A bare-bones protocol meant for imitating a single-user session with
    Hamper over stdio.
    """

    delimiter = "\n"

    def __init__(self, config):
        self.loader = PluginLoader(config)

        self.history = {}

        if 'db' in config:
            print('Loading db from config: ' + config['db'])
            db_engine = sqlalchemy.create_engine(config['db'])
        else:
            print('Using in-memory db')
            db_engine = sqlalchemy.create_engine('sqlite:///:memory:')
        DBSession = orm.sessionmaker(db_engine)
        session = DBSession()

        self.loader.db = DB(db_engine, session)

        # Load all plugins mentioned in the configuration. Allow globbing.
        print "Loading plugins", config["plugins"]
        self.loader.loadAll()

    def connectionLost(self, reason):
        if reactor.running:
            reactor.stop()

    def lineReceived(self, line):
        comm = {
            'raw_message': line,
            'message': line,
            'raw_user': "user",
            'user': "user",
            'mask': "",
            'target': "hamper",
            'channel': "hamper",
            'directed': True,
            'pm': True,
        }

        self.loader.runPlugins("chat", "message", self, comm)

    def _sendLine(self, user, message):
        if user != "hamper":
            message = "[%s] %s" % (user, message)
        self.sendLine(message)

    # Stub out some IRCClient methods

    def quit(self):
        self.stopProducing()

    def msg(self, user, message, length=None):
        for line in message.splitlines():
            self._sendLine(user, line)

    def notice(self, user, message):
        self._sendLine(user, '** ' + message)


    # CommanderProtocol methods

    def reply(self, comm, message, encode=True, tag=None, vars=[], kwvars={}):
        kwvars = kwvars.copy()
        kwvars.update(comm)
        message = message.format(*vars, **kwvars)
        if encode:
            message = message.encode('utf-8')
        self.msg(comm['channel'], message)

    # The help plugin expects bot.factory.loader to exist.
    @property
    def factory(self):
        return self


def main():
    hamper.log.setup_logging()
    config = hamper.config.load()
    StandardIO(CLIProtocol(config))
    reactor.run()


if __name__ == "__main__":
    main()
