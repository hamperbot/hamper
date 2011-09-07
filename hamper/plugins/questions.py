from random import random

from hamper.interfaces import Plugin


class Questions(Plugin):

    name = 'questions'

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
            ('Heck yes!', 'eq/2'), ("I'm sorry, I was thinking of bananas", .01),
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
                        evens.append((resp, 1.0/div))

            else:
                real_resp.append((resp, prob))
                total_prob += prob

        # Share is the probability of a "eq" probability. Share/2 would be the
        # probability of a "eq/2" probability.
        share = (1 - total_prob) / sum(div for _, div in evens)
        for resp, divisor in evens:
            real_resp.append((resp, share*divisor))

        self.responses = real_resp

    def process(self, bot, comm):
        if comm['directed'] and comm['message'].strip()[-1] == '?':
            r = random()
            for resp, prob in self.responses:
                r -= prob
                if r < 0:
                    bot.reply(comm, '{0}: {1}'.format(comm['user'], resp))
                    return True
        return False

questions = Questions()
