# -*- coding: utf-8 -*-

import random
import re

from hamper.interfaces import ChatCommandPlugin, ChatPlugin, Command
from hamper.utils import ude


class YesNoPlugin(ChatPlugin):

    name = 'yesno'
    priority = -1

    def setup(self, *args):
        """
        Set up the list of responses, with weights. If the weight of a response
        is 'eq', it will be assigned a value that splits what is left after
        everything that has a number is assigned. If it's weight is some
        fraction of 'eq' (ie: 'eq/2' or 'eq/3'), then it will be assigned
        1/2, 1/3, etc of the 'eq' weight. All probabilities will add up to
        1.0 (plus or minus any rounding errors).
        """

        responses = [
            ('Yes.', 'eq'),
            ('No.', 'eq'),
            ('Nope.', 'eq'),
            ('Maybe.', 'eq'),
            ('Possibly.', 'eq'),
            ('It could be.', 'eq'),
            ("No. No, I don't think so.", 'eq/2'),
            ('Without a doubt.', 'eq/2'),
            ('I think... Yes.', 'eq/2'),
            ('Heck yes!', 'eq/2'),
            ('Maybe. Possibly. It could be.', 'eq/2'),
            ('Ask again later.', 'eq/3'),
            ("I don't know.", 'eq/3'),
            ("I'm sorry, I was thinking of bananas", 'eq/100'),
        ]

        responses += [(x, 'eq/10') for x in (list(open('oblique.txt')))]
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
        self.is_question = re.compile('.*\?(\?|!)*$')

    def message(self, bot, comm):
        msg = ude(comm['message'].strip())
        if comm['directed'] and self.is_question.search(msg):
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
    priority = 0

    class ChoicesCommand(Command):
        regex = r'^.* or .*\?$'

        name = 'choices'
        short_desc = None
        long_desc = None

        def command(self, bot, comm, groups):
            choices = self.parse(comm['message'])

            chance_of_snark = 0.05
            snarks = [
                "I don't know, I'm just a bot",
                ['Neither', 'None of them.'],
                ['Why not both?', 'Why not all of them?'],
                [u'¿Por qué no los dos?', u'¿Por qué no los todos?'],
            ]
            snarks += list(open('obliques.txt'))

            if random.random() < chance_of_snark:
                # snark. ignore choices and choose something funny
                snark = random.choice(snarks)
                if isinstance(snarks, list):
                    conjugation = 0 if len(choices) == 2 else 1
                    choice = snark[conjugation]
                else:
                    choice = snark
            else:
                # no snark, give one of the original choices
                choice = random.choices(choices) + '.'
            bot.reply(comm, u'{0}: {1}'.format(comm['user'], choice))
            return True

        @staticmethod
        def parse(question):
            """
            Parses out choices in a 'or' based, possible comma-ed list.

            >>> parse = ChoicesPlugin.ChoicesCommand.parse
            >>> parse('x or y?')
            ['x', 'y']
            >>> parse('x, y or z?')
            ['x', 'y', 'z']
            >>> parse('this thing, that thing or the other thing?')
            ['this thing', 'that thing', 'the other thing']
            >>> parse('door or window?')
            ['door', 'window']
            >>> parse('should i do homework or play video games?')
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


if __name__ == '__main__':
    import doctest
    doctest.testmod()
