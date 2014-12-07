from gensim.corpora.wikicorpus import process_article, tokenize
from gensim.corpora.mmcorpus import MmCorpus
from gensim.corpora.dictionary import Dictionary
from gensim.models.ldamodel import LdaModel
import numpy as np
import util
import load_data
import os.path

articles = load_data.load_object("bin/article_names.pk1")

class BowCorpus(object):
    def __init__(self, fname, dictionary):
        self.filename = fname
        self.dictionary = dictionary
    def __iter__(self):
        for line in open(self.filename):
            bow = self.dictionary.doc2bow(line.lower().split())
            yield bow

def get_topics(corpus, dictionary, num_topics, lda_file):
    lda = LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics, update_every=1, chunksize=100, passes=1)
    lda.save(lda_file)
    for topic in range(10):
        print "Topic {0}: {1}".format(topic, lda.print_topic(topic))
 
# Build a dictionary of words in documents. Filters out words not used ofter
def build_dictionary(articles_file, dictionary_file):
    dictionary = Dictionary()
    for line in open(articles_file):
        dictionary.add_documents([line.lower().split()])
    #TODO Filter dictionary
    stop_ids = [dictionary.token2id[stopword] for stopword in util.STOP_WORDS if stopword in dictionary.token2id]
    dictionary.filter_tokens(stop_ids)
    dictionary.filter_extremes(no_below=2, no_above=0.5)
    dictionary.save(dictionary_file)
    return dictionary

def build_corpus(corpus_file, articles_file, dictionary):
    MmCorpus.serialize(corpus_file, BowCorpus(articles_file, dictionary))
    return MmCorpus(corpus_file)

# Combines all articles into one file. One per line
def download_articles(article_names, filename, start=0, count=100):
    with open(filename, 'a') as doc_file:
        for i in range(start, min(len(article_names), start + count)):
            article_name = article_names[i]
            print "Processing {0}: {1}".format(i, article_name)
 
            try:
                text = util.get_article_text(article_name)
                tokenized_article = tokenize(text)
                for token in tokenized_article:
                    doc_file.write("{0} ".format(token))
                doc_file.write("\n")

            except util.ArticleNotFoundError:
                print "Could not find: {0}".format(article_name)
            except:
                print "Error getting article"

download_articles(articles, "article_text.txt", 1205, 10000)
dictionary = build_dictionary("article_text.txt", "dictionary.txt")
corpus = build_corpus("corpus.mm", "article_text.txt", dictionary)
get_topics(corpus, dictionary, 10, "lda.txt")
