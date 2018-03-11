# -*- coding: latin-1 -*-

from hamper.interfaces import ChatPlugin, Command

import subprocess

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
        if comm['directed']:
            if "version" in comm['message'] and 'you' in comm['message']:
                return self.report_version(bot, comm)
        return False
