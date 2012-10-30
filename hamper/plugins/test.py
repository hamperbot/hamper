from hamper.interfaces import (ChatCommandPlugin, PresencePlugin,
                               PopulationPlugin)


class Test(ChatCommandPlugin, PresencePlugin, PopulationPlugin):
    name = "test"

    def userJoined(self, bot, user, channel):
        print('[Test] Hello {0}'.format(user))

    def userLeft(self, bot, user, channe):
        print('[Test] {0} left'.format(user))

    def userQuit(self, bot, user, quitMessage):
        print('[Test] {0} quit'.format(user))

    def userKicked(self, bot, kickee, channel, kicker, message):
        print('[Test] {0} was kicked by {1} ({2})'.format(kickee, kicker, message))

    def signedOn(self, bot):
        print('[Test] Signed on.')

    def joined(self, channel):
        print('[Test] I joined {0}'.format(channel))

    def left(self, channel):
        print('[Test] I left {0}'.format(channel))


test = Test()
