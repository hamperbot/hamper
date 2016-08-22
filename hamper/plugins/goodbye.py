import random
from hamper.interfaces import ChatPlugin

goodbyes = [
    "Goodbye",
    "Bye-bye",
    "Bye",
    "Godspeed",
    "Buhbyes",
    "Talk to you later",
    "Ta ta for now",
    "Ciao",
    "Sayanora",
    "Kamsahamnidah",
    "Unhello",
    "See ya",
    "McGoodbye",
    "May the forces of evil get lost on the way to you front doorstep",
    "Live long and prosper",
    "Cheerio!",
    "Out",
    "Y'all come back now",
    "May your teeth never be replaced by freshly ironed wool socks.",
    "So long",
    "Farewell",
    "Bon voyage",
    "May you never awaken one morning and find yourself with Iranian death camps for hands and Gorbachev's eyelids attached to your feet.",
    "Aloha",
    "L'hitraot",
    "Kol Tuv",
    "Shalom",
    "Peace out",
    "May your spleen never transform into a solution to the European Union's impending energy crisis and become a battlefield for an upcoming war to end all wars.",
    "Be well, fellow citizen",
    "I must take leave of you now",
    "Adios",
    "Arrivaderci",
    "Do svidanja",
    "Au revoir",
    "Hasta la vista",
    "Fare thee well",
    "May your mouth never be conquered by a band of marauding Vikings.",
    "Auf Wiederhören",
    "Auf Wiedersehen",
    "Servus",
    "Tschüss",
    "Tschüs",
    "Tschö",
    "Tschau",
    "Bis dann",
    "Bis bald",
    "Bis später",
    "May you never have your soul absorbed into the Netherworld by a power-hungry televangelist.",
    "Bis morgen",
    "Bis Freitagabend",
    "Bis nächste Woche",
    "God be with ye",
    "Bis zur Konferenz",
    "Bis irgendwann",
    "Kkkkk...out.",
    "Stay cool, home-brotha",
    "Tot Ziens",
    "Later days",
    "Tschuess",
    "Avrio",
    "adeus",
    "That is all.",
    "daa daa dit daa daa daa daa daa daa daa dit dit daa dit dit dit daa dit daa daa dit",
    "(*wave flags down and down-right) (*wave flags left and up-left) (*wave flags left and up-left) (*wave flags up and down) (*wave flags left and down) (*wave flags up-left and right) (*wave flags down and up-right)",
    "No more of you.",
    "SHOO! SHOO!",
    "And...I'm out.",
    "So long, and thanks for all the fish.",
    "In a while, crocodile!",
    "Uh, I can hear the voices calling me...see ya",
    "Ta-ra",
    "Cheers",
    "Fine, then go!",
    "I'm gone!",
    "Get lost",
    "Na-na-naa-na, hey hey hey, Goodbye!",
    "Pasta-and-bagels",
    "All-feet-are-the-same",
    "Olive-oil",
    "Aavjo",
    "Shalom, y'all!",
    "Hallo",
    "Later, gator!",
    "If I don't return, avenge my death!",
    "This is me. And this is the back of me.",
    "Tutloo",
    "Chevio",
    "Pip Pip",
    "See ya later, alligator",
    "Not now, brown cow",
    "'Til then, penguin",
    "Hasta mañana, iguana",
    "Tallyhoo!",
    "Timeout for now Houston",
    "Keep it between the lines...",
    "Keep it between the lines...and dirty side down",
    "Dasvedania",
    "Paka",
    "Keep it real",
    "May your mother's cousin never be assaulted by Attila the Hun at the supermarket",
    "Hasta luego",
    "Leb wohl!",
    "Mach's gut!",
    "À voir!",
    "À bientôt!",
    "Äddi!",
    "Avoir!",
    "Nos veremos.",
    "Vaarwel.",
    "Zàijiàn",
    "Zdravo",
    "Tchau",
    "Tootles",
    "Até logo",
    "Hasta la pasta",
    "Valle!",
    "Móin, móin!",
    "Xau",
    "Beijinhos",
    "Vá",
    "Abraço",
    "Fica bem",
    "Até amanhã",
    "May bad luck always be at your heels, but never catch you",
    "Xi chien",
    "TTYL",
    "C U L8R",
    "chao",
    "adichao",
    "Inabit, inabizzle.",
    "May your feet never fall off and grow back as cactuses",
    "Moi"
]


class GoodBye(ChatPlugin):
    """Be nice when someone says goodbye."""

    name = 'goodbye'
    priority = 0
    onlyDirected = False

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
                response = random.choice(goodbyes)
                bot.reply(comm, '{0[target]}: {1}'.format(comm, response))
                return True

        return False
