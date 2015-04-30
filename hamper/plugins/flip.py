# -*- coding: latin-1 -*-

from hamper.interfaces import Command, ChatCommandPlugin
import upsidedown


class Flip(ChatCommandPlugin):
    '''
    FLOSS Flip Utility
    You need to install the upsidedown package from pip to use this plugin
    '''

    name = 'flip'
    priority = 0

    class Flip(Command):
        """Deliver a quote."""
        regex = r'^flip\s(.*)$'

        name = 'flip'
        short_desc = 'flip - flip it'
        long_desc = ''

        def command(self, bot, comm, groups):
            msg = groups[0].decode('utf-8')
            angry = '(╯°□°)╯︵ '
            try:
                flip = upsidedown.transform(msg).encode('utf-8')
                ret = angry + flip
            except:
                ret = u'ಠ_ಠ'.encode('utf-8')
            bot.reply(comm, ret, encode=False)
            return True
