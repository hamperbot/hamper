import sys

from twisted.words.protocols import irc
from twisted.internet import protocol, reactor


class Commander(irc.IRCClient):

    def _get_nickname(self):
        return self.factory.nickname

    nickname = property(_get_nickname)

    def signedOn(self):
        self.join(self.factory.channel)
        print "Signed on as %s." % (self.nickname,)

    def joined(self, channel):
        print "Joined %s." % (channel,)

    def privmsg(self, user, channel, msg):
        print msg

        if not user:
            return

        if msg == '{0}: hi'.format(self.nickname):
            pretty_user = user.split('!')[0]
            self.msg(self.factory.channel, 'Hello {0}'.format(pretty_user))

        elif msg == '{0}: go away'.format(self.nickname):
            self.msg(self.factory.channel, 'Bye!')
            self.quit()

class CommanderFactory(protocol.ClientFactory):
    protocol = Commander

    def __init__(self, channel, nickname='Hamper'):
        self.channel = channel
        self.nickname = nickname

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s)." % (reason)

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason,)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        chan = sys.argv
    else:
        chan = 'hamper'

    if len(sys.argv) > 2:
        nickname = sys.argv[2]
    else:
        nickname = 'hamper'

    reactor.connectTCP('irc.freenode.net', 6667,
            CommanderFactory('#' + chan, nickname))
    reactor.run()
