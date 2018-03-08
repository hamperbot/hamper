import random
import re

from hamper.interfaces import ChatPlugin, Command
from hamper.utils import ude

platitudes = [
    "A waste of time",
    "All for one, and one for all",
    "All is fair in love and war",
    "All’s well that ends well",
    "And they all lived happily ever after",
    "At least you're not homeless.",
    "At the speed of light",
    "Better out than in",
    "Cat got your tongue?",
    "Do as I say,not as I do.",
    "Don't dwell on it.",
    "Don't let it bother you.",
    "Don't let it eat at you.",
    "Don't let it get you down.",
    "Don't let life get you down.",
    "Don't linger on the past.",
    "Don’t cry over spilt milk",
    "Don’t get your knickers in a twist",
    "Every cloud has a silver lining",
    "Everything happens for a reason.",
    "Everything's going to be OK.",
    "Frightened to death",
    "Get on with your life.",
    "Good things come to people who wait.",
    "Good things happen to those who wait.",
    "Gut-wrenching pain",
    "Happiness is a choice.",
    "Haste makes waste",
    "He has his tail between his legs",
    "Head over heels in love",
    "Heart-stopping fear",
    "I feel your pain.",
    "I share your pain.",
    "I understand this is difficult for you.",
    "If at first you don't succeed, try, try again.",
    "If life gives you lemons, make lemonade.",
    "If you can't say something nice, don't say anything at all.",
    "If you knew what I knew, you'd think differently.",
    "In a jiffy ",
    "In the nick of time",
    "It all comes out in the wash.",
    "It can't be that bad.",
    "It could be worse.",
    "It is what it is.",
    "It was just their time to go.",
    "It was meant to be.",
    "It wasn't meant to be.",
    "It will all be worth it in the end.",
    "It's God's will.",
    "It's OK.",
    "It's for your own good.",
    "It's in the past.",
    "It's not rocket science.",
    "Just a matter of time",
    "Just be yourself.",
    "Just don't think about it.",
    "Just follow your heart.",
    "Just give it time.",
    "Just think positive.",
    "Just try harder next time.",
    "Karma's a hunter2.",
    "Keep a stiff upper lip.",
    "Kiss and make up",
    "Lasted an eternity",
    "Laughter is the best medicine",
    "Let it slide off your back.",
    "Life doesn't give you things you can't handle.",
    "Live and let live.",
    "Look on the bright side.",
    "Lost track of time",
    "Love you more than life itself",
    "Maybe your heart just isn't in to it.",
    "No good deed goes unpunished.",
    "No matter what you do, it's always something.",
    "Not all that glitters is gold",
    "Nothing is impossible.",
    "One day you'll see things differently.",
    "Only time will tell",
    "Opposites attract",
    "Other people go through this every day.",
    "Our hearts go out to them",
    "Our thoughts and prayers go out to them",
    "Own it and move on.",
    "Patience is a virtue.",
    "Perception is reality.",
    "Read between the lines",
    "Rushed for time",
    "Scared out of my wits",
    "Someone woke up on the wrong side of the bed",
    "Something will turn up.",
    "Such is life.",
    "Take it one day at a time.",
    "The best revenge is to have a fulfilling life.",
    "The calm before the storm",
    "The only thing to fear is fear itself.",
    "The time of my life",
    "The writing's on the wall",
    "There is someone worse off than you.",
    "There's plenty of fish in the sea.",
    "There's somebody out there for everyone.",
    "They don't deserve you.",
    "They weren't right for you anyway.",
    "They're in a better place.",
    "Things will get easier.",
    "Things will work out.",
    "Things would be better if you were more positive.",
    "This is just a bump in the road.",
    "This is life.",
    "This too shall pass.",
    "Time heals all wounds",
    "Time heals all wounds.",
    "Time will tell.",
    "Tomorrow will be better.",
    "Tomorrow's another day.",
    "We all have problems.",
    "We all have to do things we don't want to do.",
    "We're not laughing at you we’re laughing with you",
    "What doesn't kill you makes you stronger.",
    "What goes around comes around",
    "What's done is done.",
    "When life gives you lemons, make lemonade",
    "You can be anything you want to be.",
    "You can do so much better.",
    "You did the best you could.",
    "You did this to yourself.",
    "You don't need people like that in your life.",
    "You gotta do what you gotta do.",
    "You have to know your limitations.",
    "You have to move on.",
    "You have your whole life ahead of you.",
    "You just have to try a little harder.",
    "You just haven't met the right person yet.",
    "You just need some sleep.",
    "You just need to believe in yourself.",
    "You just need to get over it.",
    "You look OK.",
    "You still have your health.",
    "You'll be OK.",
    "You'll be back in the game before you know it.",
    "You'll be better off for this.",
    "You'll be fine.",
    "You'll get better at it.",
    "You'll get over it.",
    "You'll get through it.",
    "You'll get used to it.",
    "You'll thank me for this one day.",
    "You're better off without them.",
    "You're better than this.",
    "You're lucky to be alive.",
    "You're making a mountain out of a molehill.",
    "You're paddling against the current.",
    "Your negativity is your only hurdle.",
    "Your time will come.",
    "Between a rock and a hard place",
    "Absence makes the heart grow fonder",
    "The way to someone's heart is between the third and fourth ribs",
    "Darned if you do, darned if you don't.",
]

class PlatitudesPlugin(ChatPlugin):
    """If you can't say something nice, don't say anything at all."""

    name = 'platitudes'
    priority = -3

    def setup(self, *args):
        pass

    def contemplate(self, bot, comm):
        resp = random.choice(platitudes)
        bot.reply(comm, resp)
        return True

    def inform(self, bot, comm):
        resp = random.choice(platitudes)
        bot.reply(comm, '{0}: {1}'.format(comm['user'], resp))
        return True

    def message(self, bot, comm):
        msg = ude(comm['message'].strip())
        if comm['directed']:
            if not '?' in msg:
                if random.random() < .3:
                    self.inform(bot, comm)
                else:
                    self.contemplate(bot, comm)
                return True
        elif random.random() < .0001:
            # Occasionally pipe up
            if random.random() < .2:
                self.inform(bot, comm)
            else:
                self.contemplate(bot, comm)
            return True
        return False


