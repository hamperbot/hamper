import random
from hamper.interfaces import ChatPlugin


class GoodBye(ChatPlugin):
    """Be nice when someone says goodbye."""

    name = 'goodbye'
    priority = 0
    onlyDirected = False
    responses_file = 'goodbye.txt'

    def setup(self, factory):
        # Be careful with these words, if they're something said in normal
        # conversation, it'll trigger.
        self.triggers = ['cya', 'bye', 'goodbye', 'good bye', 'farewell']

    def message(self, bot, comm):
        if (any(trigger in comm['message'] for trigger in self.triggers)
                and comm['target']):

            # TODO: Make it check Seen.users to make sure the user being
            # mentioned exists
            if comm['target']:
                response = random.choice(list(open(self.responses_file)))
                bot.reply(comm, '{0[target]}: {1}'.format(comm, response))
                return True

        return False
