# -*- coding: latin-1 -*-

from hamper.interfaces import ChatPlugin, Command

import subprocess

queues = [
    'version',
    'update',
    'kick',
    'modify',
    'reboot',
]
class SelfAwarePlugin(ChatPlugin):

    name = 'selfaware'
    priority = 1

    def report_version(self, bot, comm):
        try:
            cmd = "git log --format='%aD' -n 1 "
            process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
        except:
            return False
        if output:
            resp = "My last commit was " + output.strip("'\n")
        else:
            resp = "I have no idea."
        bot.reply(comm, '{0}: {1}'.format(comm['user'], resp))
        return True

    def message(self, bot, comm):
        msg = comm['message'].lower()
        if comm['directed']:
            if "you" in msg:
                for q in queues:
                    if q in msg:
                        return self.report_version(bot, comm)
        return False
