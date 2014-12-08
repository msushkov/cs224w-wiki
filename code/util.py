import urllib2
import json
import nltk
from HTMLParser import HTMLParser
import string
import os

STOP_WORDS_FILE = os.environ['STOP_WORDS_FILE']

# Load the English stop words
STOP_WORDS = set()
f = open(STOP_WORDS_FILE, "r")
for line in f:
    STOP_WORDS.add(line.strip())
f.close()

# the number of edges to visit when doing decentralized search before we give up
SEARCH_DIST_THRESHOLD = 100

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

# Returns a heuristic for the distance between the 2 articles.
# Things to try:
# - 1.0 / number of overlapping words
# - Jaccard similarity between 2 sets of words
# - Cosine similarity between TF-IDF vectors
def get_article_distance(article1_name, article2_name, article_text_cache):
    article1_text = None
    article2_text = None

    if article1_name in article_text_cache:
        article1_text = article_text_cache[article1_name]
    else:
        article1_text = get_article_text(article1_name)
        article_text_cache[article1_name] = article1_text

    if article2_name in article_text_cache:
        article2_text = article_text_cache[article2_name]
    else:
        article2_text = get_article_text(article2_name)
        article_text_cache[article2_name] = article2_text

    # split the text by space; convert to a set; filter stop words
    words1 = set(article1_text.split())
    words2 = set(article2_text.split())
    w1 = set([w for w in words1 if not w in STOP_WORDS])
    w2 = set([w for w in words2 if not w in STOP_WORDS])

    result = len(w1.intersection(w2))
    return (article_text_cache, result)


# Runs decentralized search
# source and destination are indices into adj_list_arg
# distance_function takes in 2 article names and a text cache dict and returns their floating-point distance
def search(src_id, dst_id, adj_list_arg, path_length, linenum_to_title, distance_function,
    visited_node_ids, article_text_cache):
    try:
        neighbors = adj_list_arg[src_id]

        # pick the best neighbor of source (the one that has the smallest distance 
        # to destination, given by distance_function)
        best_neighbor_id = None
        smallest_distance = float('inf')
        for node_id in neighbors:
            # make sure we don't visit a node more than once
            if node_id in visited_node_ids:
                continue

            node_name = linenum_to_title[str(node_id)]
            destination_name = linenum_to_title[str(dst_id)]

            try:
                (article_text_cache, curr_distance_to_dest) = distance_function(node_name,
                    destination_name, article_text_cache)

                if curr_distance_to_dest < smallest_distance:
                    best_neighbor_id = node_id
                    smallest_distance = curr_distance_to_dest

            # if we can't get the text for this article, skip it
            except ArticleNotFoundError:
                continue

        visited_node_ids.add(src_id)

        if best_neighbor_id != None:
            print linenum_to_title[str(best_neighbor_id)]

        if best_neighbor_id == None:
            return ("FAILURE", -2)
        elif best_neighbor_id == dst_id:
            return ("SUCCESS", path_length + 1)
        else:
            if path_length >= SEARCH_DIST_THRESHOLD:
                # didn't find after searching for a while
                return ("FAILURE", path_length + 1)
            else:
                return search(best_neighbor_id, dst_id, adj_list_arg, path_length + 1,\
                    linenum_to_title, distance_function, visited_node_ids, article_text_cache)
    except KeyError:
        print "sr_id = %d, dst_id = %d, neighbors of src = %s" % (src_id, dst_id, str(adj_list_arg[src_id]))
        raise KeyError

# Wrapper for search()
def run_decentralized_search(src_id, dst_id, adj_list, linenum_to_title, distance_function):
    print "Running decentralized search..."

    # cache the src and dst article text first; if one of them isnt found, don't bother with the search
    src_name = linenum_to_title[str(src_id)]
    dst_name = linenum_to_title[str(dst_id)]

    src_text = None
    dst_text = None

    article_text_cache = {}

    try:
        src_text = get_article_text(src_name)
        dst_text = get_article_text(dst_name)

        article_text_cache[src_name] = src_text
        article_text_cache[dst_name] = dst_text
    except ArticleNotFoundError:
        return ("FAILURE", -1)

    try:
        return search(src_id, dst_id, adj_list, 0, linenum_to_title, distance_function, 
            set(), article_text_cache)
    except KeyError:
        print "In run_decentralized_search(): KeyError in search()"
        return (None, None)

