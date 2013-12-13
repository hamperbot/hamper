from fnmatch import fnmatch

from twisted.internet import reactor
from twisted.internet.stdio import StandardIO
from twisted.protocols.basic import LineReceiver
from twisted.plugin import getPlugins

import sqlalchemy
from sqlalchemy import orm

from hamper.commander import DB, PluginLoader
import hamper.config
from hamper.interfaces import BaseInterface
import hamper.log
import hamper.plugins


class CLIProtocol(LineReceiver):
    """
    A bare-bones protocol meant for imitating a single-user session with
    Hamper over stdio.
    """

    delimiter = "\n"

    def __init__(self, config):
        self.loader = PluginLoader()
        self.loader.config = config

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
        plugins = getPlugins(BaseInterface, package=hamper.plugins)
        for plugin in plugins:
            for pattern in config["plugins"]:
                if fnmatch(plugin.name, pattern):
                    self.loader.registerPlugin(plugin)

    def connectionLost(self, reason):
        reactor.stop()

    def lineReceived(self, line):
        comm = {
            'raw_message': line,
            'message': line,
            'raw_user': "user",
            'user': "user",
            'target': "hamper",
            'channel': "hamper",
            'directed': True,
            'pm': True,
        }

        self.loader.runPlugins("chat", "message", self, comm)

    def reply(self, comm, message):
        print "Sending", message
        self.sendLine(message)


def main():
    hamper.log.setup_logging()
    config = hamper.config.load()
    StandardIO(CLIProtocol(config))
    reactor.run()


if __name__ == "__main__":
    main()
