import re

from hamper.interfaces import ChatCommandPlugin, Command

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

SQLAlchemyBase = declarative_base()


class Karma(ChatCommandPlugin):
    '''Give, take, and scoreboard Internet Points'''

    """
    Hamper will look for lines that end in ++ or -- and modify that user's
    karma value accordingly

    !karma --top: shows (at most) the top 5
    !karma --bottom: shows (at most) the bottom 5
    !karma <username>: displays the karma for a given user

    NOTE: The user is just a string, this really could be anything...like
    potatoes or the infamous cookie clicker....
    """

    name = 'karma'

    priority = -2

    short_desc = 'Give or take karma from someone'
    long_desc = ('username++ - Give karma\n'
                 'username-- - Take karma\n'
                 '!karma --top - Show the top 5 karma earners\n'
                 '!karma --bottom - Show the bottom 5 karma earners\n'
                 '!karma username - Show the user\'s karma count\n')

    gotta_catch_em_all = r"""# 3 or statement
                             (

                             # Starting with a (, look for anything within
                             # parens that end with 2 or more + or -
                             (?=\()[^\)]+\)(\+\++|--+) |

                             # Looking from the start of the line until 2 or
                             # more - or + are found. No whitespace in this
                             # grouping
                             ^[^\s]+(\+\++|--+) |

                             # Finally group any non-whitespace groupings
                             # that end with 2 or more + or -
                             [^\s]+?(\+\++|--+)((?=\s)|(?=$))
                            )
                          """

    regstr = re.compile(gotta_catch_em_all, re.X)

    def setup(self, loader):
        super(Karma, self).setup(loader)
        self.db = loader.db
        SQLAlchemyBase.metadata.create_all(self.db.engine)

    def message(self, bot, comm):
        """
        Check for strings ending with 2 or more '-' or '+'
        """
        super(Karma, self).message(bot, comm)

        # No directed karma giving or taking
        if not comm['directed']:
            msg = comm['message'].strip().lower()
            # use the magic above
            words = self.regstr.findall(msg)
            # Do things to people
            karmas = self.modify_karma(words)
            # Commit karma changes to the db
            self.update_db(karmas)

    def modify_karma(self, words):
        """
        Given a regex object, look through the groups and modify karma
        as necessary
        """
        # I don't want to type this all the time, k?
        kt = self.db.session.query(KarmaTable)

        # 'user': karma
        k = {}

        if words:
            # For loop through all of the group members
            for word_tuple in words:
                word = word_tuple[0]
                ending = word[-1]
                # This will either end with a - or +, if it's a - subract 1 kara,
                # if it ends with a +, add 1 karma
                change = -1 if ending == '-' else 1
                # Now strip the ++ or -- from the end
                if '-' in ending:
                    word = word.rstrip('-')
                elif '+' in ending:
                    word = word.rstrip('+')
                # Check if surrounded by parens, if so, remove them
                if word.startswith('(') and word.endswith(')'):
                    word = word[1:-1]
                # Add the user to the dict
                if word:
                    k[word] = change
        return k

    def update_db(self, userkarma):
        """
        Change the users karma by the karma amount (either 1 or -1)
        """

        kt = self.db.session.query(KarmaTable)
        for user in userkarma:
            # Modify the db accourdingly
            urow = kt.filter(KarmaTable.user == user).first()
            # If the user doesn't exist, create it
            if not urow:
                urow = KarmaTable(user)
            urow.kcount += userkarma[user]
            self.db.session.add(urow)
        self.db.session.commit()

    class KarmaList(Command):
        """
        Return the top or bottom 5
        """

        regex = r'^(?:score|karma) --(top|bottom)$'

        LIST_MAX = 5

        def command(self, bot, comm, groups):
            users = bot.factory.loader.db.session.query(KarmaTable)
            user_count = users.count()
            top = self.LIST_MAX if user_count >= self.LIST_MAX else user_count

            if top:
                show = (KarmaTable.kcount.desc() if groups[0] == 'top'
                        else KarmaTable.kcount)
                for user in users.order_by(show)[0:top]:
                    bot.reply(comm, str('%s\x0f: %d' % (user.user, user.kcount)))
            else:
                bot.reply(comm, r'No one has any karma yet :-(')

    class UserKarma(Command):
        """
        Retrieve karma for a given user
        """

        # !karma <username>
        regex = r'^(?:score|karma) ([^-].+)$'

        def command(self, bot, comm, groups):
            # Play nice when the user isn't in the db
            kt = bot.factory.loader.db.session.query(KarmaTable)
            user = kt.filter(KarmaTable.user == groups[0].lower()).first()

            if user:
                bot.reply(comm, str('%s\x0f: %d' % (user.user, user.kcount)))
            else:
                bot.reply(comm, str("No karma for %s\x0f" % groups[0].lower()))


class KarmaTable(SQLAlchemyBase):
    """
    Keep track of users karma in a persistant manner
    """

    __tablename__ = 'karma'

    # Calling the primary key user, though, really, this can be any string
    user = Column(String, primary_key=True)
    kcount = Column(Integer)

    def __init__(self, user, kcount=0):
        self.user = user
        self.kcount = kcount


karma = Karma()
