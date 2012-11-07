import random

from hamper.interfaces import ChatCommandPlugin, ChatPlugin, Command


class YesNoPlugin(ChatPlugin):

    name = 'yesno'
    priority = -1

    def setup(self, *args):
        """
        Set up the list of responses, with weights. If the weight of a response
        is 'eq', it will be assigned equal value after everything that has a
        number is assigned. If it's weight is some fraction of 'eq' (ie: 'eq/2'
        or 'eq/3'), then it will be assigned 1/2, 1/3, etc of the 'eq' weight.
        All probabilities will up to 1.0 (plus/minus any rounding errors).
        """

        responses = [
            ('I think... Yes.', 'eq'), ('Maybe. Possibly. It could be.', 'eq'),
            ("No. No, I don't think so.", 'eq'), ("I don't know.", 'eq'),
            ('Ask again later.', 'eq/2'), ('Without a doubt.', 'eq/2'),
            ('Heck yes!', 'eq/2'), ("I'm sorry, I was thinking of bananas", .03),
        ]

        total_prob = 0
        real_resp = []
        evens = []
        for resp, prob in responses:
            if isinstance(prob, str):
                if prob.startswith('eq'):
                    sp = prob.split('/')
                    if len(sp) == 1:
                        evens.append((resp, 1))
                    else:
                        div = int(sp[1])
                        evens.append((resp, 1.0 / div))

            else:
                real_resp.append((resp, prob))
                total_prob += prob

        # Share is the probability of a "eq" probability. Share/2 would be the
        # probability of a "eq/2" probability.
        share = (1 - total_prob) / sum(div for _, div in evens)
        for resp, divisor in evens:
            real_resp.append((resp, share * divisor))

        self.responses = real_resp

    def message(self, bot, comm):
        if comm['directed'] and comm['message'].strip()[-1] == '?':
            r = random.random()
            for resp, prob in self.responses:
                r -= prob
                if r < 0:
                    bot.reply(comm, '{0}: {1}'.format(comm['user'], resp))
                    return True
        return False


class ChoicesPlugin(ChatCommandPlugin):
    """
    Answers questions like "apples or bananas?" "this, that or the other
    things", and "should I do homework or play videogames?"
    """

    name = 'choices'
    priority = 1

    class ChoicesCommand(Command):
        regex = r'^.* or .*$'

        name = 'choices'
        short_desc = None
        long_desc = None

        def command(self, bot, comm, groups):
            choices = self.parse(comm['message'])
            choice = random.choice(choices) + '.'
            print choices
            if random.random() <= 0.05:
                choice = "Neither."
            bot.reply(comm, '{0}: {1}'.format(comm['user'], choice))

        @staticmethod
        def parse(question):
            """
            Parses out choices in a 'or' based, possible comma-ed list.

            >>> ChoicesPlugin.ChoicesCommand.parse('x or y?')
            ['x', 'y']
            >>> ChoicesPlugin.ChoicesCommand.parse('x, y or z?')
            ['x', 'y', 'z']
            >>> ChoicesPlugin.ChoicesCommand.parse('this thing, that thing or the other thing?')
            ['this thing', 'that thing', 'the other thing']
            >>> ChoicesPlugin.ChoicesCommand.parse('door or window?')
            ['door', 'window']
            >>> ChoicesPlugin.ChoicesCommand.parse('should i do homework or play video games?')
            ['do homework', 'play video games']
            """
            # Handle things like "should ___ X or Y"
            if question.lower().startswith('should'):
                question = ' '.join(question.split()[2:])

            question = question.strip('?')
            # split on both ',' and ' or '
            choices = question.split(',')
            choices = sum((c.split(' or ') for c in choices), [])
            # Get rid of empty strings
            choices = filter(bool, (c.strip() for c in choices))
            return choices


yesno = YesNoPlugin()
choices = ChoicesPlugin()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
