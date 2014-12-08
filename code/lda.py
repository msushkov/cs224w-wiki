from gensim.corpora.wikicorpus import process_article, tokenize
from gensim.corpora.mmcorpus import MmCorpus
from gensim.corpora.dictionary import Dictionary
from gensim.models.ldamodel import LdaModel
from gensim.models.tfidfmodel import TfidfModel
import numpy as np
import os.path
import wiki_index
from scipy import linalg, mat, dot

NUM_TOPICS = 10

DICTIONARY_FILE = os.environ['DICTIONARY_FILE']
CORPUS_FILE = os.environ['CORPUS_FILE']
LDA_FILE_10 = os.environ['LDA_FILE_10']
LDA_FILE_30 = os.environ['LDA_FILE_30']
LDA_FILE_60 = os.environ['LDA_FILE_60']
LDA_FILE_120 = os.environ['LDA_FILE_120']
TFIDF_FILE = os.environ['TFIDF_FILE']

class BowCorpus(object):
    def __init__(self, fname, dictionary):
        self.filename = fname
        self.dictionary = dictionary
    def __iter__(self):
        for line in open(self.filename):
            bow = self.dictionary.doc2bow(line.lower().split())
            yield bow

def get_tfidf_for_doc(document):
    bow = dictionary.doc2bow(document)
    return tfidf[bow]

def get_tfidf_for_article_name(article_name):
    bow = dictionary.doc2bow(wiki_index.get_article(article_name))
    return tfidf[bow]

def get_tfidf_model():
    if os.path.isfile(TFIDF_FILE):
        return TfidfModel.load(TFIDF_FILE)
    else:
        model = TfidfModel(get_corpus(), get_dictionary())
        model.save(TFIDF_FILE)
        return model

def get_lda_model(num_topics):
    file_name = None

    if num_topics == 10:
        file_name = LDA_FILE_10
    elif num_topics == 30:
        file_name = LDA_FILE_30
    elif num_topics == 60:
        file_name = LDA_FILE_60
    elif num_topics == 120:
        file_name = LDA_FILE_120
    else:
        raise ValueError("bad number of topics")

    return LdaModel.load(file_name)

def get_dictionary():
    return Dictionary.load(DICTIONARY_FILE)

def get_corpus():
    return MmCorpus(CORPUS_FILE)

def get_topics_for_article_name(article_name):
    article = wiki_index.get_article(article_name)
    doc_bow = dictionary.doc2bow(article)
    return lda[doc_bow]

# If corpus and dictionary are None then it takes them from files.
# Returns the lda model object (after saving it to a file).
def build_lda_model(corpus, dictionary, num_topics=10):
    if corpus == None:
        corpus = get_corpus()
    if dictionary == None:
        dictionary = get_dictionary()

    if num_topics == 10:
        file_name = LDA_FILE_10
    elif num_topics == 30:
        file_name = LDA_FILE_30
    elif num_topics == 60:
        file_name = LDA_FILE_60
    elif num_topics == 120:
        file_name = LDA_FILE_120
    else:
        raise ValueError("bad number of topics")
    lda = LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics, update_every=1, chunksize=100, passes=1)
    lda.save(file_name)
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


# Compute cosine similarity between 2 topic vectors
# Each topic vector is a list of tuples: (topic_id, prob)
def get_cosine_sim(vec1, vec2, num_topics):
    x1 = cos_sim_helper(vec1, num_topics)
    x2 = cos_sim_helper(vec2, num_topics)
    return cos_sim(x1, x2)

# Input: list of (topic_id, prob)
# Output: list of probabilities for each of the topics (including 0s)
def cos_sim_helper(vec, num_topics):
    result = [0.0] * num_topics
    for (topic_id, prob) in vec:
        result[topic_id] = prob
    return result

def cos_sim(v1, v2):
    a = mat(v1)
    b = mat(v2)
    return float(dot(a,b.T)/linalg.norm(a)/linalg.norm(b))


# Create variables
if not os.path.isfile(DICTIONARY_FILE) or not os.path.isfile(CORPUS_FILE):
    print "Building dictionary..."
    dictionary = build_dictionary()
    print dictionary
    print "Building corpus..."
    corpus = build_corpus(dictionary)
    print corpus
    print "Building lda model..."
    lda = build_lda_model(corpus, dictionary, NUM_TOPICS)
    print "Done"
else:
    print "Loading dictionary..."
    dictionary = get_dictionary()
    print "Loading corpus..."
    corpus = get_corpus()
    print "Loading lda model..."
    lda = get_lda_model(NUM_TOPICS)

print "Loading tfidf..."
tfidf = get_tfidf_model()

