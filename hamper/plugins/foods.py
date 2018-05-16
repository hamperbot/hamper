import random

from hamper.interfaces import ChatPlugin
from hamper.utils import ude

foodverbs = [
    "bake",
    "order",
    "fry",
    "steam",
    "boil",
    "simmer",
    "blend",
    "eat",
    "nosh",
    "nibble",
    "snack on",
    "nom",
    "chomp",
    "consume",
]

foodtools = [
    "blender",
    "frying pan",
    "colander",
    "kettle",
    "pot",
    "plate",
    "knife",
    "fork",
    "spoon",
    "sous vide",
    "crockpot",
    "whipping siphon",
    "spatula",
    "tray",
]

foodunits = [
    "bag",
    "box",
    "carton",
    "can",
    "jar",
    "package",
    "piece",
    "bottle",
    "bar",
]

foodqualities = [
    "acidic",
    "bland",
    "creamy",
    "fatty",
    "fruity",
    "healthy",
    "nutty",
    "oily",
    "raw",
    "salty",
    "sharp",
    "sour",
    "spicy",
    "sweet",
    "tender",
    "tough",
    "huge",
    "tiny",
    "spoiled",
]

ingredients = [
    "dairy",
    "fish",
    "fruit",
    "anchovy",
    "apple",
    "apricot",
    "artichoke",
    "asparagus",
    "bacon",
    "banana",
    "beans",
    "beef",
    "blackberry",
    "blackcurrant",
    "blueberry",
    "bread",
    "broccoli",
    "brownies",
    "buffalo",
    "butter",
    "carrot",
    "cauliflower",
    "celery",
    "cereal",
    "cheese",
    "cherry",
    "chicken",
    "chocolate",
    "coconut",
    "cod",
    "coffee",
    "cooked meat",
    "cream",
    "creams",
    "cucumber",
    "duck",
    "egg",
    "eggplant",
    "fig",
    "garlic",
    "ginger",
    "gooseberry",
    "grape",
    "grapefruit",
    "grapes",
    "haddock",
    "ham",
    "herring",
    "kidney",
    "kiwi",
    "kiwi fruit",
    "lamb",
    "leek",
    "lemon",
    "lettuce",
    "lime",
    "liver",
    "mackerel",
    "mango",
    "melon",
    "milk",
    "mince",
    "mushroom",
    "olive",
    "onion",
    "orange",
    "peach",
    "peanut",
    "pear",
    "peas",
    "pepper",
    "pineapple",
    "plum",
    "pomegranate",
    "pork",
    "potato",
    "pumpkin",
    "quark",
    "radish",
    "raspberry",
    "redcurrant",
    "rhubarb",
    "rye",
    "salami",
    "salmon",
    "sausages",
    "strawberry",
    "sweet potato",
    "trout",
    "tuna",
    "turkey",
    "veal",
    "vegetable",
    "walnut",
    "water",
    "wheat",
    "yoghurt",
]

foodpreparations = [
    "casserole",
    "burrito",
    "lasagne",
    "porridge",
    "pie",
    "cake",
    "wrap",
    "salad",
    "ice cream",
    "tea",
    "wine",
    "beer",
    "juice",
    "soda",
    "roll",
    "sandwich",
    "stir-fry",
    "soup",
    "pasta",
    "pizza",
]

meals = [
    "elvensies",
    "second breakfast",
    "lunch",
    "breakfast",
    "afternoon tea",
    "dinner",
    "supper",
    "a snack",
    "a midnight snack",
    "your cheat meal",
]

additives = [
    "basil",
    "chives",
    "coriander",
    "dill",
    "parsley",
    "rosemary",
    "sage",
    "thyme",
    "spices",
    "chilli powder",
    "cinnamon",
    "cumin",
    "curry powder",
    "nutmeg",
    "paprika",
    "saffron",
    "ketchup",
    "mayonnaise",
    "mustard",
    "pepper",
    "salad dressing",
    "salt",
    "vinaigrette",
    "vinegar",
]

suggestions = [
    "how about you",
    "I recommend you",
    "perhaps you should",
    "maybe you could",
    "just",
    "better not",
    "why not just",
]

discussors = [
    " eat ",
    "food",
    "hungry",
    "lunch",
    "dinner",
    "breakfast",
    "snack",
]

class FoodsPlugin(ChatPlugin):
    """Even robots can get peckish"""

    name = 'foods'
    priority = 0

    def setup(self, *args):
        pass

    def articleize(self, noun):
        if random.random() < .3:
            noun = random.choice(foodunits) + " of " + noun
        if noun[0] in ['a', 'e', 'i', 'o', 'u', 'y']:
            return "an " + noun
        return "a " + noun

    def discusses_food(self, msg):
        for d in discussors:
            if d in msg:
                return d.strip() + "? "
        return False

    def describe_ingredient(self):
        """ apple. tart apple with vinegar. """
        resp = random.choice(ingredients)
        if random.random() < .2:
            resp = random.choice(foodqualities) + " " + resp
        if random.random() < .2:
            resp += " with " + self.describe_additive()
        return resp

    def describe_additive(self):
        """ vinegar. spicy vinegar. a spicy vinegar. """
        resp = random.choice(additives)
        if random.random() < .2:
           resp = random.choice(foodqualities) + ' ' + resp
        if random.random() < .01:
           resp = self.articleize(resp)
        return resp

    def describe_dish(self):
        """a burrito. a lettuce burrito with ketchup and raspberry."""
        resp = random.choice(foodpreparations)
        if random.random() < .85:
            resp = self.describe_ingredient() + ' ' + resp
            if random.random() < .2:
                resp = self.describe_ingredient() + ' and ' + resp
                if random.random() < .2:
                    resp = self.describe_ingredient() + ', ' + resp
        if random.random() < .5:
            resp += " with " + self.describe_additive()
        elif random.random() < .5:
            resp += " with " + self.describe_ingredient()
        return self.articleize(resp)

    def describe_meal(self):
        resp = self.describe_dish()
        if random.random() < .1:
            resp += ", and " + self.describe_meal()
        return resp

    def suggest(self):
        resp = self.describe_meal()
        if random.random() < .7:
            resp = random.choice(foodverbs) + ' ' + resp
            if random.random() < .5:
                resp = random.choice(suggestions) + ' ' + resp
            if random.random() < .3:
                resp += random.choice([' made with ', ' on ', ' using '])
                resp += self.articleize(random.choice(foodtools))
        return resp

    def foodyreply(self, bot, comm, prefix = ""):
        resp = prefix + self.suggest()
        bot.reply(comm, '{0}: {1}'.format(comm['user'], resp))

    def message(self, bot, comm):
        msg = ude(comm['message'].strip())
        prefix = self.discusses_food(msg)
        if prefix:
            if comm['directed']:
                # always reply on question or comment to self about food
                self.foodyreply(bot, comm)
            elif random.random() < .7:
                # often interject anyways
                self.foodyreply(bot, comm, prefix)
            return True
        return False

