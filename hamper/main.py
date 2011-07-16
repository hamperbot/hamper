import sys
import yaml

from twisted.words.protocols import irc
from twisted.internet import protocol, reactor

from hamper import commands
from hamper.commander import CommanderFactory


if __name__ == '__main__':

    config = yaml.load(open('hamper.conf'))

    reactor.connectTCP(config['server'], config['port'],
            CommanderFactory(config['channel'], config['nickname']))
    reactor.run()
