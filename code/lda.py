from gensim.corpora.wikicorpus import process_article, tokenize
from gensim.corpora.mmcorpus import MmCorpus
from gensim.corpora.dictionary import Dictionary
from gensim.models.ldamodel import LdaModel
import numpy as np
import util
import load_data
import os.path
import wiki_index

DICTIONARY_FILE = os.environ['DICTIONARY_FILE']
CORPUS_FILE = os.environ['CORPUS_FILE']
LDA_FILE = os.environ['LDA_FILE']

class BowCorpus(object):
    def __init__(self, fname, dictionary):
        self.filename = fname
        self.dictionary = dictionary
    def __iter__(self):
        for line in open(self.filename):
            bow = self.dictionary.doc2bow(line.lower().split())
            yield bow

def get_lda_model():
    return lda.load(LDA_FILE)

def get_dictionary():
    return dictionary.load(DICTIONARY_FILE)

def get_topics_for_article_name(article_name, lda_model, dictionary, article_name_to_linenum):
    article = wiki_index.get_article(article_name, article_name_to_linenum)
    doc_bow = dictionary.doc2bow(article)
    return lda_model[doc_bow]

def get_topics(corpus, dictionary, num_topics):
    lda = LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics, update_every=1, chunksize=100, passes=1)
    lda.save(LDA_FILE)
    for topic in range(10):
        print "Topic {0}: {1}".format(topic, lda.print_topic(topic))
    return lda
 
# Build a dictionary of words in documents. Filters out words not used ofter
def build_dictionary():
    dictionary = Dictionary()
    for line in open(wiki_index.ARTICLES_FILE):
        dictionary.add_documents([line.lower().split()])
    dictionary.filter_extremes(no_below=2, no_above=0.5)
    dictionary.save(DICTIONARY_FILE)
    return dictionary

def build_corpus(dictionary):
    MmCorpus.serialize(CORPUS_FILE, BowCorpus(wiki_index.ARTICLES_FILE, dictionary))
    return MmCorpus(CORPUS_FILE)

if not os.path.isfile(DICTIONARY_FILE) or not os.path.isfile(CORPUS_FILE) or not os.path.isfile(LDA_FILE):
    dictionary = build_dictionary()
    print dictionary
    corpus = build_corpus(dictionary)
    get_topics(corpus, dictionary, 10)
