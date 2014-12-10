import urllib2
import json
import nltk
from HTMLParser import HTMLParser
import string
import os
import wiki_index
import lda
import random

STOP_WORDS_FILE = os.environ['STOP_WORDS_FILE']

# Load the English stop words
STOP_WORDS = set()
f = open(STOP_WORDS_FILE, "r")
for line in f:
    STOP_WORDS.add(line.strip())
f.close()

# the number of edges to visit when doing decentralized search before we give up
SEARCH_DIST_THRESHOLD = 500

BASE_REQUEST_STR = "http://en.wikipedia.org/w/api.php?action=query&prop=extracts&format=json&explaintext&exsectionformat=plain&rvprop=content&titles="


# Strips HTML tags from a string. Copied from StackOverflow.
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


# example request:
# http://en.wikipedia.org/w/api.php?action=query&prop=extracts&format=json&explaintext&exsectionformat=plain&rvprop=content&titles=Barack%20Obama
def create_wiki_api_url(article_name):
    new_name = article_name.replace(" ", "%20")
    return BASE_REQUEST_STR + new_name


class ArticleNotFoundError(Exception):
    pass
    #def __init__(self, article_name):
    #    self.article_name = article_name
    #def __str__(self):
    #    return self.article_name

# Get the text of a single Wikipedia article
def get_article_text(article_name):
    if "&" in article_name:
        article_name = article_name.replace("&", "%26")

    result = urllib2.urlopen(create_wiki_api_url(article_name)).read()

    data = json.loads(result)

    d = data["query"]["pages"]
    key = d.keys()[0]
    if "extract" not in d[key]:
        raise ArticleNotFoundError(article_name)

    s = d[key]["extract"].encode("utf-8", "ignore")
    
    # remove HTML tags
    clean_text = strip_tags(s)

    # remove punctuation
    result = clean_text.translate(None, string.punctuation)
    
    #tokens = nltk.word_tokenize(strip_tags(s))
    
    return result.lower()


# Get the height of a node in the ontology tree given its article name.
def get_height(article_name, type_to_depth, name_to_type):
    try:
        curr_type = name_to_type[article_name]
        return type_to_depth[curr_type]
    except KeyError:
        print "ARTICLE: " + str(article_name)
        print "TYPE: " + str(name_to_type[article_name])
        print type_to_depth[curr_type]
        return None

# Get the path length through the lowest common ancestor in the ontology tree.
# Returns a tuple of (dist, lca_height)
def get_ontology_distance(article1_name, article2_name, name_to_type, type_to_depth, type_to_node):
    article1_height = get_height(article1_name, type_to_depth, name_to_type)
    article2_height = get_height(article2_name, type_to_depth, name_to_type)

    article1_type_node = type_to_node[name_to_type[article1_name]]
    article2_type_node = type_to_node[name_to_type[article2_name]]

    lca_height = get_height(lowest_common_ancestor(type_to_node["ROOT"], \
        article1_type_node, article2_type_node), type_to_depth, name_to_type)

    return (abs(float(lca_height) - article1_height) + \
        abs(float(lca_height) - article2_height), lca_height)

# append the string names to path
def get_path(root, node, path):
    path.append(root.value)

    if root.value != node.value:
        for child in root.get_children():
            get_path(child, node, path)
    else:
        return path

# Get the path from root to both nodes; then find the point at which
# they start to diverge.
# node1 and node2 are both nodes in the ontology tree.
def lowest_common_ancestor(root, node1, node2):
    path1 = get_path(root, node1, [])
    path2 = get_path(root, node2, [])

    min_index = min(len(path1), len(path2))
    last_equal = None
    for i in range(min_index):
        x1 = path1[i]
        x2 = path2[i]

        if x1 == x2:
            last_equal = x1
        else:
            return last_equal


# Returns a heuristic for the distance between the 2 articles.
# Things to try:
# - 1.0 / number of overlapping words
# - Jaccard similarity between 2 sets of words
# - Cosine similarity between TF-IDF vectors
def get_article_distance(article1_name, article2_name):
    #print "Article 1: %s, article 2: %s" % (article1_name, article2_name)

    #article1_text = None
    #article2_text = None

    article1_text = wiki_index.get_article(article1_name)
    article2_text = wiki_index.get_article(article2_name)

    # split the text by space; convert to a set; filter stop words
    #article1_words = set(article1_text)
    #article2_words = set(article2_text)

    # feature 1 = 1.0 / number of non-stop words in common
    # feature 2 = 1.0 / Jaccard similarity
    # feature 3 = 1.0 / cos sim between tfidf vectors
    # feature 4 = Hellinger distance between LDA distr

    #size_int = float(len(article1_words.intersection(article2_words)))
    #feat1 = size_int

    #size_union = float(len(article1_words.union(article2_words)))
    #feat2 = size_int / size_union
    
    # feature 3: tf idf cosine sim
    # vec1 = lda.get_tfidf_for_doc(article1_text)
    # vec2 = lda.get_tfidf_for_doc(article2_text)
    # feat3 = lda.get_cosine_sim(vec1, vec2)

    # feature 4: hellinger dist
    vec1 = lda.get_topics_for_article_text(article1_text, 10)
    vec2 = lda.get_topics_for_article_text(article2_text, 10)
    feat4 = lda.get_hellinger(vec1, vec2, 10)

    return feat4

    # result = feat3
    # if result > 0:
    #     return 1.0 / result
    # else:
    #     return 100000.0



# Returns a list of NLP features for these articles.
def extract_nlp_features(article1_name, article2_name, num_lda_topics, name_to_type, type_to_depth, type_to_node):
    article_name_to_linenum = wiki_index.get_article_name_to_linenum()

    # lists of words
    article1_text = wiki_index.get_article(article1_name)
    article2_text = wiki_index.get_article(article2_name)

    return get_features(article1_name, article2_name, article1_text, article2_text, num_lda_topics, name_to_type, type_to_depth, type_to_node)

# Input: 2 lists of words
def get_features(article1_name, article2_name, article1_words, article2_words, num_lda_topics, name_to_type, type_to_depth, type_to_node):
    features = []

    # feature 1: number of words in overlap (Jaccard sim)
    size_int = float(len(set(article1_words).intersection(set(article2_words))))
    size_union = float(len(set(article1_words).union(set(article2_words))))
    feat1 = size_int / size_union
    features.append(feat1)

    # feature 2: lda - Hellinger distance betwene topic distributions
    vec1 = lda.get_topics_for_article_text(article1_words, num_lda_topics)
    vec2 = lda.get_topics_for_article_text(article2_words, num_lda_topics)
    feat2 = lda.get_hellinger(vec1, vec2, num_lda_topics)
    features.append(feat2)

    # feature 3: TF-IDF - cosine sim
    vec1 = lda.get_tfidf_for_doc(article1_words)
    vec2 = lda.get_tfidf_for_doc(article2_words)
    feat3 = lda.get_cosine_sim(vec1, vec2)
    features.append(feat3)

    # feature 4: num words of article 1
    features.append(len(article1_words))

    # feature 5: num words of article 2
    features.append(len(article2_words))

    return features

    # new_features = []

    # for f in features:
    #     new_features.append(f)
    #     new_features.append(f * f)

    # return new_features


# Runs decentralized search
# source and destination are indices into adj_list_arg
# distance_function takes in 2 article names and a text cache dict and returns their floating-point distance
def search(src_id, dst_id, adj_list_arg, path_length, linenum_to_title, distance_function, visited_node_ids):
    if src_id not in adj_list_arg:
        return ("FAILURE", -2)

    neighbors = adj_list_arg[src_id]

    if len(neighbors) == 0:
        return ("FAILURE", -2)

    is_random = False

    # feature 2: take neighbor with largest degree
    # feature 3: take neighbor with smallest degree

    # pick the best neighbor of source (the one that has the smallest distance 
    # to destination, given by distance_function)
    best_neighbor_id = None
    smallest_distance = float('inf')    

    if is_random:
        best_neighbor_id = random.choice(neighbors)
    else:
        for node_id in neighbors:
            # make sure we don't visit a node more than once
            if node_id in visited_node_ids:
                continue

            node_name = linenum_to_title[str(node_id)]
            destination_name = linenum_to_title[str(dst_id)]

            try:
                curr_distance_to_dest = distance_function(node_name, destination_name)

                if curr_distance_to_dest < smallest_distance:
                    best_neighbor_id = node_id
                    smallest_distance = curr_distance_to_dest

            # if we can't get the text for this article, skip it
            except KeyError:
                continue

    visited_node_ids.add(src_id)

    if best_neighbor_id == None:
        # dead end
        return ("FAILURE", -2)
    elif best_neighbor_id == dst_id:
        return ("SUCCESS", path_length + 1)
    else:
        if path_length >= SEARCH_DIST_THRESHOLD:
            # didn't find after searching for a while
            return ("FAILURE", -1)
        else:
            return search(best_neighbor_id, dst_id, adj_list_arg, path_length + 1,\
                linenum_to_title, distance_function, visited_node_ids)

# Wrapper for search()
def run_decentralized_search(src_id, dst_id, adj_list, linenum_to_title, distance_function):
    # article_text_cache = {}

    # article1_name = linenum_to_title[str(src_id)]
    # article2_name = linenum_to_title[str(dst_id)]

    # article1_text = wiki_index.get_article(article1_name)
    # article2_text = wiki_index.get_article(article2_name)

    # article_text_cache[article1_name] = article1_text
    # article_text_cache[article2_name] = article2_text

    return search(src_id, dst_id, adj_list, 0, linenum_to_title, distance_function, set())
