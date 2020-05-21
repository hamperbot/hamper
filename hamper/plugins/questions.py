# -*- coding: utf-8 -*-

import random
import re

from hamper.interfaces import ChatCommandPlugin, ChatPlugin, Command
from hamper.utils import ude

betwords = [
    "bet",
    "odds",
    "chances",
    "wager",
    "gamble",
    "probability",
    "likelihood",
]

idcall = [
    "I'd call the odds ",
    "The odds are ",
    "Chances might be ",
]

foragainst = [
    "of ",
    "for ",
    "against ",
]

bettings = [
    "Across the board",
    "Act of God",
    "As good luck would have it",
    "Back the field",
    "Bet your bottom dollar",
    "Bread always falls buttered side down",
    "Copper-bottomed",
    "Dead ringer",
    "Don't count your chickens before they are hatched",
    "Draw a blank",
    "Eeny, meeny, miny, mo",
    "Hedge your bets",
    "Second-guess",
    "Take potluck",
    "Third time lucky",
    "Turn the tables",
]

adjs = ["able",
    "acid",
    "angry",
    "automatic",
    "awake",
    "bad",
    "beautiful",
    "bent",
    "bitter",
    "black",
    "blue",
    "boiling",
    "bright",
    "broken",
    "brown",
    "certain",
    "cheap",
    "chemical",
    "chief",
    "clean",
    "clear",
    "cold",
    "common",
    "complete",
    "complex",
    "conscious",
    "cruel",
    "cut",
    "dark",
    "dead",
    "dear",
    "deep",
    "delicate",
    "dependent",
    "different",
    "dirty",
    "dry",
    "early",
    "elastic",
    "electric",
    "equal",
    "false",
    "fat",
    "feeble",
    "female",
    "fertile",
    "first",
    "fixed",
    "flat",
    "free",
    "frequent",
    "full",
    "future",
    "general",
    "good",
    "gray",
    "great",
    "green",
    "hanging",
    "happy",
    "hard",
    "healthy",
    "high",
    "hollow",
    "ill",
    "important",
    "kind",
    "last",
    "late",
    "left",
    "like",
    "living",
    "long",
    "loose",
    "loud",
    "low",
    "male",
    "married",
    "material",
    "medical",
    "military",
    "mixed",
    "narrow",
    "natural",
    "necessary",
    "new",
    "normal",
    "old",
    "open",
    "opposite",
    "parallel",
    "past",
    "physical",
    "political",
    "poor",
    "possible",
    "present",
    "private",
    "public",
    "quick",
    "quiet",
    "ready",
    "red",
    "regular",
    "responsible",
    "right",
    "rough",
    "round",
    "sad",
    "safe",
    "same",
    "second",
    "secret",
    "separate",
    "serious",
    "sharp",
    "short",
    "shut",
    "simple",
    "slow",
    "small",
    "smooth",
    "soft",
    "solid",
    "special",
    "sticky",
    "stiff",
    "straight",
    "strange",
    "strong",
    "sudden",
    "sweet",
    "tall",
    "thick",
    "thin",
    "tight",
    "tired",
    "true",
    "violent",
    "waiting",
    "warm",
    "wet",
    "white",
    "wide",
    "wise",
    "wrong",
    "yellow",
    "young",
    ]

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
    "A line has two sides.",
    "Balance the consistency principle with the inconsistency principle.",
    "Breathe more deeply.",
    "Bridges: -build, -burn.",
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
    ("Make an exhaustive list of everything you might do and do the last "
        "thing on the list."),
    "Make a sudden, destructive, unpredictable action; incorporate.",
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


nouns = ["angle",
     "ant",
     "apple",
     "arch",
     "arm",
     "army",
     "baby",
     "bag",
     "ball",
     "band",
     "basin",
     "basket",
     "bath",
     "bed",
     "bee",
     "bell",
     "berry",
     "bird",
     "blade",
     "board",
     "boat",
     "bone",
     "book",
     "boot",
     "bottle",
     "box",
     "boy",
     "brain",
     "brake",
     "branch",
     "brick",
     "bridge",
     "brush",
     "bucket",
     "bulb",
     "button",
     "cake",
     "camera",
     "card",
     "carriage",
     "cart",
     "cat",
     "chain",
     "cheese",
     "chess",
     "chin",
     "church",
     "circle",
     "clock",
     "cloud",
     "coat",
     "collar",
     "comb",
     "cord",
     "cow",
     "cup",
     "curtain",
     "cushion",
     "dog",
     "door",
     "drain",
     "drawer",
     "dress",
     "drop",
     "ear",
     "egg",
     "engine",
     "eye",
     "face",
     "farm",
     "feather",
     "finger",
     "fish",
     "flag",
     "floor",
     "fly",
     "foot",
     "fork",
     "fowl",
     "frame",
     "garden",
     "girl",
     "glove",
     "goat",
     "gun",
     "hair",
     "hammer",
     "hand",
     "hat",
     "head",
     "heart",
     "hook",
     "horn",
     "horse",
     "hospital",
     "house",
     "island",
     "jewel",
     "kettle",
     "key",
     "knee",
     "knife",
     "knot",
     "leaf",
     "leg",
     "library",
     "line",
     "lip",
     "lock",
     "map",
     "match",
     "monkey",
     "moon",
     "mouth",
     "muscle",
     "nail",
     "neck",
     "needle",
     "nerve",
     "net",
     "nose",
     "nut",
     "office",
     "orange",
     "oven",
     "parcel",
     "pen",
     "pencil",
     "picture",
     "pig",
     "pin",
     "pipe",
     "plane",
     "plate",
     "plough",
     "pocket",
     "pot",
     "potato",
     "prison",
     "pump",
     "rail",
     "rat",
     "receipt",
     "ring",
     "rod",
     "roof",
     "root",
     "sail",
     "school",
     "scissors",
     "screw",
     "seed",
     "sheep",
     "shelf",
     "ship",
     "shirt",
     "shoe",
     "skin",
     "skirt",
     "snake",
     "sock",
     "spade",
     "sponge",
     "spoon",
     "spring",
     "square",
     "stamp",
     "star",
     "station",
     "stem",
     "stick",
     "stocking",
     "stomach",
     "store",
     "street",
     "sun",
     "table",
     "tail",
     "thread",
     "throat",
     "thumb",
     "ticket",
     "toe",
     "tongue",
     "tooth",
     "town",
     "train",
     "tray",
     "tree",
     "trousers",
     "umbrella",
     "wall",
     "watch",
     "wheel",
     "whip",
     "whistle",
     "window",
     "wing",
     "wire",
     "worm",
]

canstarts = [
    "Yes, you'll need ",
    "Yes, but watch out for ",
    "Maybe if you had ",
    "Nope, there's too much of ",
    "Never! Insufficient ",
    "Perhaps try with ",
]

affirmatives = [
    ' do ',
    'Heck yes!',
    'I think... Yes.',
    'It could be.',
    'Maybe.',
    'Possibly.',
    'Without a doubt.',
    'Yes.',
    'does the pope... er, is this the right channel?'
    'mhmm',
    'right',
    'sure',
    'yeah',
    'yes',
    'you said it',
    'yup',
    'yus',
]

negatories = [
    "don't",
    'no',
    'nope',
    'nerp',
    'never',
    'nah',
    'NEVAR',
    'Nope.',
    'No.',
    'Eww.',
    'No. No, no way',
    'That would be negatory.',
    'Why would anyone?',
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
            ('How should I know?', 'eq'),
            ('Try asking a human', 'eq/10'),
            ('Eww.', 'eq'),
            ('You\'d just do the opposite of whatever I tell you', 'eq/50'),
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
        responses += [(i.strip(), 'eq') for i in affirmatives]
        responses += [(i.strip(), 'eq') for i in negatories]
        self.advices = [(x, 1) for x in obliques]
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

    def shouldq(self, bot, comm):
        resp = random.choice(obliques)
        bot.reply(comm, '{0}: {1}'.format(comm['user'], resp))
        return True

    def articleize(self, noun):
        if random.random() < .3:
            noun = random.choice(adjs) + ' ' + noun
        if noun[0] in ['a', 'e', 'i', 'o', 'u', 'y']:
            return "an " + noun
        return "a " + noun

    def canq(self, bot, comm):
        resp = random.choice(canstarts)
        resp += self.articleize(random.choice(nouns))
        if random.random() < .5:
                resp += " and " + self.articleize(random.choice(nouns))
        if random.random() < .1:
                resp += " and " + self.articleize(random.choice(nouns))
        resp += random.choice(['...', '.', '?'])
        bot.reply(comm, '{0}: {1}'.format(comm['user'], resp))
        return True

    def xtoy(self):
        x = str(int(random.random()*10))
        y = str(int(random.random()*10))
        return x + " to " + y

    def manything(self, msg):
        parts = msg.split()
        quantifiers = ['many', 'much']
        for q in quantifiers:
            if q in msg:
                idx = parts.index(q)
                for i in range(idx, len(parts)):
                    if len(parts[i]) > 4:
                        # Let's pretend to plural.
                        return parts[i].rstrip('s') + 's'
        return None

    def howmany(self, bot, comm, msg):
        thing = self.manything(msg)
        resp = random.randint(-5, 100)
        if resp > 80:
            resp = random.randint(80, 1000)
        resp = str(resp)
        if resp == '0':
            if thing:
                resp = "No " + thing + " at all."
            else:
                resp = "None at all."
        if thing:
            if resp == '1':
                resp = "Just a single " + thing.rstrip('s')
            else:
                resp += " " + thing
        if random.random() < .05:
            if thing:
                resp = "All the " + thing + "!"
            else:
                resp = "All of them!"
        bot.reply(comm, resp)
        return True

    def betting(self, bot, comm):
        resp = random.choice(bettings)
        if random.random() < .7:
            resp = random.choice(idcall)
            resp += random.choice(foragainst)
            resp += random.choice(['it ','that ','such nonsense ', 'such a thing '])
            resp += self.xtoy()
        bot.reply(comm, resp)
        return True

    def hamperesque(self, bot, comm, msg):
            whatsay = ""
            if "n't" in msg:
                whatsay = random.choice(negatories)
            for n in negatories:
                if n in msg:
                    whatsay = random.choice(negatories)
            for a in affirmatives:
                if a in msg:
                    whatsay = random.choice(affirmatives)
            if "n't" in msg:
                whatsay = random.choice(negatories)
            if whatsay != "":
                bot.reply(comm, '{0}: {1}'.format(comm['user'], whatsay))
            else:
                r = random.random()
                replies = self.responses
                for resp, prob in replies:
                    r -= prob
                    if r < 0:
                        bot.reply(comm, '{0}: {1}'.format(comm['user'], resp))
                        return True

    def sortq(self, bot, comm, msg):
        if "should " in msg:
            return self.shouldq(bot, comm)
        for b in betwords:
            if b in msg:
                return self.betting(bot, comm)
        if "can " in msg or "could" in msg:
            return self.canq(bot, comm)
        if "many" in msg or "much" in msg:
            # TODO handle "much" with units
            return self.howmany(bot, comm, msg)
        return self.hamperesque(bot, comm, msg)

    def message(self, bot, comm):
        msg = ude(comm['message'].strip()).lower()
        if self.is_question.search(msg):
            if comm['directed']:
                self.sortq(bot, comm, msg)
            elif random.random() < .1:
                self.sortq(bot, comm, msg)
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
            print choices
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
                choice = random.choice(choices) + '.'
            print choice
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
