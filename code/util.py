import urllib2
import json
import nltk
from HTMLParser import HTMLParser
import string
from nltk.corpus import stopwords
import load_data

# The English stop words
STOP_WORDS = set(stopwords.words('english'))

# the number of edges to visit when doing decentralized search before we give up
SEARCH_DIST_THRESHOLD = 1000

BASE_REQUEST_STR = "http://en.wikipedia.org/w/api.php?action=query&prop=extracts&format=json&titles="


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
# http://en.wikipedia.org/w/api.php?action=query&prop=extracts&format=json&titles=Barack%20Obama
def create_wiki_api_url(article_name):
    new_name = article_name.replace(" ", "%20")
    return BASE_REQUEST_STR + new_name

# Get the text of a single Wikipedia article
def get_article_text(article_name):
    result = urllib2.urlopen(create_wiki_api_url(article_name)).read()
    
    data = json.loads(result)
    d = data["query"]["pages"]
    key = d.keys()[0]
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
def get_article_distance(article1_name, article2_name):
    article1_text = get_article_text(article1_name)
    article2_text = get_article_text(article2_name)

    # split the text by space; convert to a set; filter stop words
    words1 = set(article1_text.split())
    words2 = set(article2_text.split())
    w1 = set([w for w in words1 if not w in STOP_WORDS])
    w2 = set([w for w in words2 if not w in STOP_WORDS])

    result = len(w1.intersection(w2))
    return result


# Runs decentralized search
# source and destination are indices into adj_matrix_arg
# similarity_function takes in 2 indices (in adj_matrix_arg) of nodes and returns a floating-point distance between them
def search(source, destination, adj_matrix_arg, path_length, distance_function):
    #neighbors = get_neighbors(source, adj_matrix_arg)
    neighbors = adj_matrix_arg[source]

    # pick the best neighbor of source (the one that has the smallest distance to destination, given by distance_function)
    best_neighbor = None
    smallest_distance = float('inf')
    for node in neighbors:
        (node_name, destination_name) = load_data.convert_adj_ids_to_article_names(node, destination)
        curr_distance_to_dest = distance_function(node_name, destination_name)
        if curr_distance_to_dest < smallest_distance:
            best_neighbor = node
            smallest_distance = curr_distance_to_dest
    if best_neighbor == destination:
        return ("SUCCESS", path_length + 1)
    else:
        if path_length >= SEARCH_DIST_THRESHOLD:
            # didn't find after searching for a while
            return ("FAILURE", path_length + 1)
        else:
            return search(best_neighbor, destination, adj_matrix_arg, path_length + 1, distance_function)

# Wrapper for search()
def run_decentralized_search(source_article_name, dest_article_name):
    title_to_linenum = load_data.load_object("bin/title_to_linenum.pk1")
    edges_id_to_adj_index = load_data.load_object("bin/edges_id_to_adj_index.pk1")
    adj_matrix = load_data.load_object("bin/adj_matrix.pk1")
    
    try:
        src_linenum = title_to_linenum[source_article_name]
        dst_linenum = title_to_linenum[dest_article_name]

        src_adj_index = edges_id_to_adj_index[src_linenum]
        dst_adj_index = edges_id_to_adj_index[dst_linenum]

        return search(src_adj_index, dst_adj_index, adj_matrix, 0, load_data.get_ontology_distance)
    except KeyError:
        return (None, None)
        
# The distance function to be used in search()
def distance(adj_matrix_id1, adj_matrix_id2):
    (article1_name, article2_name) = load_data.convert_adj_ids_to_article_names(adj_matrix_id1, adj_matrix_id2)
    return get_article_distance(article1_name, article2_name)

