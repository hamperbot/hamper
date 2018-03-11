from nltk.classify import NaiveBayesClassifier
from nltk.corpus import subjectivity
from nltk.sentiment import SentimentAnalyzer, SentimentIntensityAnalyzer
from nltk.sentiment.util import *

import re
from collections import defaultdict

from hamper.interfaces import ChatCommandPlugin, Command
from hamper.utils import ude, uen

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

SQLAlchemyBase = declarative_base()


class Mood(ChatCommandPlugin):
    """
    The things I hear and see, they change how I feel!
    """

    name = 'mood'

    priority = 3

    def setup(self, loader):
        print "getting moody..."
        n_instances = 100
        subj_docs = [(sent, 'subj') for sent in
        subjectivity.sents(categories='subj')[:n_instances]]
        obj_docs = [(sent, 'obj') for sent in
        subjectivity.sents(categories='obj')[:n_instances]]
        train_subj_docs = subj_docs[:80]
        test_subj_docs = subj_docs[80:100]
        train_obj_docs = obj_docs[:80]
        test_obj_docs = obj_docs[80:100]
        training_docs = train_subj_docs+train_obj_docs
        testing_docs = test_subj_docs+test_obj_docs
        sentim_analyzer = SentimentAnalyzer()
        all_words_neg = sentim_analyzer.all_words([mark_negation(doc) for doc in training_docs])
        unigram_feats = sentim_analyzer.unigram_word_feats(all_words_neg, min_freq=4)
        sentim_analyzer.add_feat_extractor(extract_unigram_feats, unigrams=unigram_feats)
        training_set = sentim_analyzer.apply_features(training_docs)
        test_set = sentim_analyzer.apply_features(testing_docs)
        trainer = NaiveBayesClassifier.train
        classifier = sentim_analyzer.train(trainer, training_set)
        self.sid = SentimentIntensityAnalyzer()
        print "mood got"
        self.db = loader.db
        SQLAlchemyBase.metadata.create_all(self.db.engine)

    def message(self, bot, comm):
        msg = comm['message'].strip().lower()
        ss = self.sid.polarity_scores(msg)
        self.update_mood(comm['user'], ss)
        print ss

    def update_mood(self, fren, ss):
        kt = self.db.session.query(MoodTable)
        urow = kt.filter(MoodTable.fren == ude(fren)).first()
        if not urow:
            urow = MoodTable(ude(fren))
        urow.latest = ss
        urow.downers += ss['neg']
        urow.uppers += ss['pos']
        urow.mixed += ss['compound']
        urow.meh += ss['neu']
        self.db.session.add(urow)
        self.db.session.commit()
#
#    class KarmaList(Command):
#        """
#        Return the top or bottom 5
#        """
#
#        regex = r'^(?:score|karma) --(top|bottom)$'
#
#        LIST_MAX = 5
#
#        def command(self, bot, comm, groups):
#            users = bot.factory.loader.db.session.query(KarmaTable)
#            user_count = users.count()
#            top = self.LIST_MAX if user_count >= self.LIST_MAX else user_count
#
#            if top:
#                show = (KarmaTable.kcount.desc() if groups[0] == 'top'
#                        else KarmaTable.kcount)
#                for user in users.order_by(show)[0:top]:
#                    bot.reply(
#                        comm, str('%s\x0f: %d' % (user.user, user.kcount))
#                    )
#            else:
#                bot.reply(comm, r'No one has any karma yet :-(')
#
#    class UserKarma(Command):
#        """
#        Retrieve karma for a given user
#        """
#
#        # !karma <username>
#        regex = r'^(?:score|karma)\s+([^-].*)$'
#
#        def command(self, bot, comm, groups):
#            # Play nice when the user isn't in the db
#            kt = bot.factory.loader.db.session.query(KarmaTable)
#            thing = ude(groups[0].strip().lower())
#            user = kt.filter(KarmaTable.user == thing).first()
#
#            if user:
#                bot.reply(
#                    comm, '%s has %d points' % (uen(user.user), user.kcount),
#                    encode=False
#                )
#            else:
#                bot.reply(
#                    comm, 'No karma for %s ' % uen(thing), encode=False
#                )
#

class MoodTable(SQLAlchemyBase):
    """
    Keep track of my mood toward users in a persistant manner
    """

    __tablename__ = 'mood'

    # Calling the primary key fren, though, really, this can be any string
    fren = Column(String, primary_key=True)
    uppers = Column(Integer)
    downers = Column(Integer)
    mixed = Column(Integer)
    meh = Column(Integer)
    latest = Column(Dict)

    def __init__(self, fren, latest={'neg': 0, 'neu': 0, 'pos': 0, 'compound': 0}):
        self.fren = fren
        self.uppers = latest['pos']
        self.downers = latest['neg']
        self.mixed = latest['compound']
        self.meh = latest['neu']
        self.latest = latest


karma = Karma()
