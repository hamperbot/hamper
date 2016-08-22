# -*- coding: utf-8 -*-

import random
import re

from hamper.interfaces import ChatCommandPlugin, ChatPlugin, Command
from hamper.utils import ude

obliques = [
    "Turn it over.",
    "Switch the axes.",
    "Think about color.",
    "Make it black and white.",
    "Use the tangents.",
    "Move across the room.",
    "Restart.",
    "Make it ridiculous.",
    "Stop making sense.",
    "Emphasize the side effects.",
    "Turn it into a game.",
    "More semicolons.",
    "Apply the Sieve of Eratosthenes.",
    "Try faking it.",
    "State the problem in words as clearly as possible.",
    "Only one element of each kind.",
    "What would your closest friend do?",
    "What to increase? What to reduce?",
    "Are there sections? Consider transitions.",
    "Don't think. Do.",
    "But, does it float?",
    "Remove half.",
    "Abandon normal instruments.",
    "Accept advice.",
    "Accretion.",
    "A line has two sides.",
    "Balance the consistency principle with the inconsistency principle.",
    "Breathe more deeply.",
    "Bridges -build -burn.",
    "Cascades.",
    "Cluster analysis.",
    "Consider different fading systems.",
    "Courage!",
    "Cut a vital connection.",
    "Decorate, decorate.",
    "Define an area as 'safe' and use it as an anchor.",
    "Destroy the most important thing.",
    "Discard an axiom.",
    "Disconnect from desire.",
    "Discover the recipes you are using and abandon them.",
    "Distorting time.",
    "Don't be afraid of things because they're easy to do.",
    "Don't be frightened of cliches.",
    "Don't be frightened to display your talents.",
    "Don't stress one thing more than another.",
    "Do something boring.",
    "Do the washing up.",
    "Do the words need changing?",
    "Do we need holes?",
    "Emphasize differences.",
    "Emphasize repetitions.",
    "Emphasize the flaws.",
    "Get your neck massaged.",
    "Give way to your worst impulse.",
    "Go slowly all the way round the outside.",
    "Honor thy error as a hidden intention.",
    "How would you have done it?",
    "Humanize something free of error.",
    "Infinitesimal gradations.",
    "Into the impossible.",
    "Is it finished?",
    "Is there something missing?",
    "Just carry on.",
    "Left channel, right channel, centre channel.",
    "Look at a very small object, look at its centre.",
    "Look at the order in which you do things.",
    "Look closely at the most embarrassing details and amplify them.",
    "Make a blank valuable by putting it in an exquisite frame.",
    "Make an exhaustive list of everything you might do and do the last thing on",
    "the list.",
    "Make a sudden, destructive unpredictable action; incorporate.",
    "Only one element of each kind.",
    "Remember those quiet evenings.",
    "Remove ambiguities and convert to specifics.",
    "Remove specifics and convert to ambiguities.",
    "Repetition is a form of change.",
    "Reverse.",
    "Simple subtraction.",
    "Spectrum analysis.",
    "Take a break.",
    "Take away the elements in order of apparent non-importance.",
    "Tidy up.",
    "Turn it upside down.",
    "Twist the spine.",
    "Use an old idea.",
    "Use an unacceptable color.",
    "Water.",
    "What are you really thinking about just now? Incorporate.",
    "What is the reality of the situation?",
    "What mistakes did you make last time?",
    "What wouldn't you do?",
    "Work at a different speed.",
    "Take a walk.",
    "Take a shower.",
    "Look to Nature.",
    "Talk it through with a friend.",
    "Who's your audience?",
    "Forget the money, make it cool."
]


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

        responses += [(x, 'eq/10') for x in obliques]
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
            snarks += obliques

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
