import re
from collections import Counter, defaultdict
from datetime import datetime

from hamper.interfaces import ChatCommandPlugin, Command
from hamper.utils import ude, uen

import pytz
from pytz import timezone
from pytz.exceptions import UnknownTimeZoneError

from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base

SQLAlchemyBase = declarative_base()


class Karma(ChatCommandPlugin):
    '''Give, take, and scoreboard Internet Points'''

    """
    Hamper will look for lines that end in ++ or -- and modify that user's
    karma value accordingly

    NOTE: The user is just a string, this really could be anything...like
    potatoes or the infamous cookie clicker....
    """

    name = 'karma'

    priority = -2

    short_desc = ("karma - Give positive or negative karma. Where you see"
                  " !karma, !score will work as well")
    long_desc = ("username++ - Give karma\n"
                 "username-- - Take karma\n"
                 "!karma --top - Show the top 5 karma earners\n"
                 "!karma --bottom - Show the bottom 5 karma earners\n"
                 "!karma --giver or --taker - Show who's given the most"
                 " positive or negative karma\n"
                 "!karma --when-positive or --when-negative "
                 " - Show when people are the most positive or negative\n"
                 "!karma username - Show the user's karma count\n")

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

        # Config
        config = loader.config.get("karma", {})
        self.timezone = config.get('timezone', 'UTC')
        try:
            self.tzinfo = timezone(self.timezone)
        except UnknownTimeZoneError:
            self.tzinfo = timezone('UTC')
            self.timezone = 'UTC'

    def message(self, bot, comm):
        """
        Check for strings ending with 2 or more '-' or '+'
        """
        super(Karma, self).message(bot, comm)

        # No directed karma giving or taking
        if not comm['directed'] and not comm['pm']:
            msg = comm['message'].strip().lower()
            # use the magic above
            words = self.regstr.findall(msg)
            # Do things to people
            karmas = self.modify_karma(words)
            # Notify the users they can't modify their own karma
            if comm['user'] in karmas.keys():
                if karmas[comm['user']] <= 0:
                    bot.reply(comm, "Don't be so hard on yourself.")
                else:
                    bot.reply(comm, "Tisk, tisk, no up'ing your own karma.")
            # Commit karma changes to the db
            self.update_db(comm["user"], karmas)

    def modify_karma(self, words):
        """
        Given a regex object, look through the groups and modify karma
        as necessary
        """

        # 'user': karma
        k = defaultdict(int)

        if words:
            # For loop through all of the group members
            for word_tuple in words:
                word = word_tuple[0]
                ending = word[-1]
                # This will either end with a - or +, if it's a - subract 1
                # kara, if it ends with a +, add 1 karma
                change = -1 if ending == '-' else 1
                # Now strip the ++ or -- from the end
                if '-' in ending:
                    word = word.rstrip('-')
                elif '+' in ending:
                    word = word.rstrip('+')
                # Check if surrounded by parens, if so, remove them
                if word.startswith('(') and word.endswith(')'):
                    word = word[1:-1]
                # Finally strip whitespace
                word = word.strip()
                # Add the user to the dict
                if word:
                    k[word] += change
        return k

    def update_db(self, giver, receiverkarma):
        """
        Record a the giver of karma, the receiver of karma, and the karma
        amount. Typically the count will be 1, but it can be any positive or
        negative integer.
        """

        for receiver in receiverkarma:
            if receiver != giver:
                urow = KarmaStatsTable(ude(giver), ude(receiver),
                                       receiverkarma[receiver])
                self.db.session.add(urow)
        self.db.session.commit()

    class KarmaList(Command):
        """
        Return the highest or lowest 5 receivers of karma
        """

        regex = r'^(?:score|karma) --(top|bottom)$'

        LIST_MAX = 5

        def command(self, bot, comm, groups):
            # Let the database restrict the amount of rows we get back.
            # We can then just deal with a few rows later on
            session = bot.factory.loader.db.session
            kcount = func.sum(KarmaStatsTable.kcount).label('kcount')
            kts = session.query(KarmaStatsTable.receiver, kcount) \
                         .group_by(KarmaStatsTable.receiver)

            # For legacy support
            classic = session.query(KarmaTable)

            # Counter for sorting and updating data
            counter = Counter()

            if kts.count() or classic.count():
                # We should limit the list of users to at most self.LIST_MAX
                if groups[0] == 'top':
                    classic_q = classic.order_by(KarmaTable.kcount.desc())\
                                       .limit(self.LIST_MAX).all()
                    query = kts.order_by(kcount.desc())\
                               .limit(self.LIST_MAX).all()

                    counter.update(dict(classic_q))
                    counter.update(dict(query))
                    snippet = counter.most_common(self.LIST_MAX)
                elif groups[0] == 'bottom':
                    classic_q = classic.order_by(KarmaTable.kcount)\
                                       .limit(self.LIST_MAX).all()
                    query = kts.order_by(kcount)\
                               .limit(self.LIST_MAX).all()
                    counter.update(dict(classic_q))
                    counter.update(dict(query))
                    snippet = reversed(counter.most_common(self.LIST_MAX))
                else:
                    bot.reply(
                        comm, r'Something went wrong with karma\'s regex'
                    )
                    return

                for rec in snippet:
                    bot.reply(
                        comm, '%s\x0f: %d' % (uen(rec[0]), rec[1]),
                        encode=False
                    )
            else:
                bot.reply(comm, 'No one has any karma yet :-(')

    class UserKarma(Command):
        """
        Retrieve karma for a given user
        """

        # !karma <username>
        regex = r'^(?:score|karma)\s+([^-].*)$'

        def command(self, bot, comm, groups):
            # The receiver (or in old terms, user) of the karma being tallied
            receiver = ude(groups[0].strip().lower())

            # Manage both tables
            sesh = bot.factory.loader.db.session

            # Old Table
            kt = sesh.query(KarmaTable)
            user = kt.filter(KarmaTable.user == receiver).first()

            # New Table
            kst = sesh.query(KarmaStatsTable)
            kst_list = kst.filter(KarmaStatsTable.receiver == receiver).all()

            # The total amount of karma from both tables
            total = 0

            # Add karma from the old table
            if user:
                total += user.kcount

            # Add karma from the new table
            if kst_list:
                for row in kst_list:
                    total += row.kcount

            # Pluralization
            points = "points"
            if total == 1 or total == -1:
                points = "point"

            # Send the message
            bot.reply(
                comm, '%s has %d %s' % (uen(receiver), total, points),
                encode=False
            )

    class KarmaGiver(Command):
        """
        Identifies the person who gives the most karma
        """

        regex = r'^(?:score|karma) --(giver|taker)$'

        def command(self, bot, comm, groups):
            kt = bot.factory.loader.db.session.query(KarmaStatsTable)
            counter = Counter()

            if groups[0] == 'giver':
                positive_karma = kt.filter(KarmaStatsTable.kcount > 0)
                for row in positive_karma:
                    counter[row.giver] += row.kcount

                m = counter.most_common(1)
                most = m[0] if m else None
                if most:
                    bot.reply(
                        comm,
                        '%s has given the most karma (%d)' %
                        (uen(most[0]), most[1])
                    )
                else:
                    bot.reply(
                        comm,
                        'No positive karma has been given yet :-('
                    )
            elif groups[0] == 'taker':
                negative_karma = kt.filter(KarmaStatsTable.kcount < 0)
                for row in negative_karma:
                    counter[row.giver] += row.kcount

                m = counter.most_common()
                most = m[-1] if m else None
                if most:
                    bot.reply(
                        comm,
                        '%s has given the most negative karma (%d)' %
                        (uen(most[0]), most[1])
                    )
                else:
                    bot.reply(
                        comm,
                        'No negative karma has been given yet'
                    )

    class MostActive(Command):
        """
        Least/Most active hours of karma giving/taking

        This will now look in the config for a timezone to use when displaying
        the hour.

        Example
        Karma:
            timezone: America/Los_Angeles

        If no timezone is given, or it's invalid, time will be reported in UTC
        """

        regex = r'^(?:score|karma)\s+--when-(positive|negative)'

        def command(self, bot, comm, groups):
            kt = bot.factory.loader.db.session.query(KarmaStatsTable)
            counter = Counter()

            if groups[0] == "positive":
                karma = kt.filter(KarmaStatsTable.kcount > 0)
            elif groups[0] == "negative":
                karma = kt.filter(KarmaStatsTable.kcount < 0)

            for row in karma:
                hour = row.datetime.hour
                counter[hour] += row.kcount

            common_hour = (counter.most_common(1)[0][0]
                           if counter.most_common(1) else None)

            # Title case for when
            title_case = groups[0][0].upper() + groups[0][1:]

            if common_hour:
                # Create a datetime object
                current_time = datetime.now(pytz.utc)
                # Give it the common_hour
                current_time = current_time.replace(hour=int(common_hour))
                # Get the localized common hour
                hour = self.plugin.tzinfo.normalize(
                    current_time.astimezone(self.plugin.tzinfo)).hour
                # Report to the channel
                bot.reply(
                    comm,
                    '%s karma is usually given during the %d:00 hour (%s)' %
                    (title_case, hour, self.plugin.timezone)
                )
            else:
                # Inform that no karma of that type has been awarded yet
                bot.reply(
                    comm,
                    '%s karma has been given yet' % title_case
                )


class KarmaTable(SQLAlchemyBase):
    """
    Bringing back the classic table so data doesn't need to be dumped
    """

    __tablename__ = 'karma'

    # Karma Classic Table
    user = Column(String, primary_key=True)
    kcount = Column(Integer)

    def __init__(self, user, kcount):
        self.user = user
        self.kcount = kcount


class KarmaStatsTable(SQLAlchemyBase):
    """
    Keep track of users karma in a persistant manner
    """

    __tablename__ = 'karmastats'

    # Calling the primary key user, though, really, this can be any string
    id = Column(Integer, primary_key=True)
    giver = Column(String)
    receiver = Column(String)
    kcount = Column(Integer)
    datetime = Column(DateTime, default=datetime.utcnow())

    def __init__(self, giver, receiver, kcount):
        self.giver = giver
        self.receiver = receiver
        self.kcount = kcount
