import sys
import re

from twisted.words.protocols import irc
from twisted.internet import protocol, reactor


class Commander(irc.IRCClient):

    commands = []

    def _get_nickname(self):
        return self.factory.nickname

    nickname = property(_get_nickname)

    def signedOn(self):
        self.join(self.factory.channel)
        print "Signed on as %s." % (self.nickname,)

    def joined(self, channel):
        print "Joined %s." % (channel,)

    def privmsg(self, user, channel, msg):
        print msg,

        if not user:
            return

        directed = msg.startswith(self.nickname)
        if directed:
            msg = re.match(self.nickname + r'[:,]? *(.*)', msg).groups()[0]

        print 'directed: ', directed

        for cmd in Commander.commands:
            if cmd[0].match(msg):
                if (directed and cmd[2]) or (not cmd[2]):
                    cmd[1](self, user, msg)

    def say(self, msg):
        self.msg(self.factory.channel, msg)


class CommanderFactory(protocol.ClientFactory):

    protocol = Commander

    def __init__(self, channel, nickname='Hamper'):
        self.channel = channel
        self.nickname = nickname

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s)." % (reason)

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason,)


def registerCommand(regex, directed=True):
    regex = re.compile(regex, re.IGNORECASE)

    def register(Command):
        Commander.commands.append((regex, Command(), directed))

    return register


@registerCommand('hi')
class FriendlyCommand(object):

    def __call__(self, commander, user, message):
        commander.say('Hello {0}'.format(user))


@registerCommand('go away')
class QuitCommand(object):

    def __call__(self, commander, user, message):
        commander.say('Bye!')
        commander.quit()
        reactor.stop()

@registerCommand('.*pon(y|ies).*', False)
class OmgPonies(object):

    def __call__(self, commander, user, message):
        commander.say('OMG PONIES!!!')

@registerCommand('.*lmgtfy\s+(.*)', False)
class LetMeGoogleThatForYou(object):
    def __call__(self, commander, user, message):
        regex = r'.*lmgtfy\s+(.*)\s*'
        match = re.match(regex, message, re.IGNORECASE).groups()[0]
        commander.say('http://lmgtfy.com/?q=' + match)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        chan = sys.argv[1]
    else:
        chan = 'hamper'

    if len(sys.argv) > 2:
        nickname = sys.argv[2]
    else:
        nickname = 'hamper'

    reactor.connectTCP('irc.freenode.net', 6667,
            CommanderFactory('#' + chan, nickname))
    reactor.run()
