from hamper.interfaces import Command, ChatCommandPlugin


class WhatWasThat(ChatCommandPlugin):
    '''
    What Was That?

    Give details about the last thing that was said.
    '''

    name = 'whatwasthat'
    priority = 2

    class WhatWasThat(Command):
        regex = r'^what\s*was\s*that\??$'

        name = 'whatwasthat'
        short_desc = 'whatwasthat - Say what hamper did last'
        long_desc = ''

        def command(self, bot, comm, groups):
            sent_messages = bot.factory.sent_messages.get(comm['channel'], [])
            if sent_messages:
                last = sent_messages[-1]
                if last['tag']:
                    bot.reply(comm, '{user}: That was {0}'
                                    .format(last['tag'], **comm))
                else:
                    bot.reply(comm, "{user}: I'm not sure why I said that."
                                    .format(**comm))
            else:
                bot.reply(comm, "I didn't do it!")
            return True
