import urllib2
import json
import nltk
from HTMLParser import HTMLParser
import string
from nltk.corpus import stopwords

# The English stop words
STOP_WORDS = set(stopwords.words('english'))

# the number of edges to visit when doing decentralized search before we give up
SEARCH_DIST_THRESHOLD = 100

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
# source and destination are indices into adj_list_arg
# distance_function takes in 2 article names and returns their floating-point distance
def search(src_id, dst_id, adj_list_arg, path_length, linenum_to_title, distance_function, visited_node_ids):
    try:
        neighbors = adj_list_arg[src_id]
        print len(neighbors)

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

            curr_distance_to_dest = distance_function(node_name, destination_name)
            if curr_distance_to_dest < smallest_distance:
                best_neighbor_id = node_id
                smallest_distance = curr_distance_to_dest

        visited_node_ids.add(src_id)

        print linenum_to_title[str(best_neighbor_id)]

        if best_neighbor_id == dst_id:
            return ("SUCCESS", path_length + 1)
        else:
            if path_length >= SEARCH_DIST_THRESHOLD:
                # didn't find after searching for a while
                return ("FAILURE", path_length + 1)
            else:
                return search(best_neighbor_id, dst_id, adj_list_arg, path_length + 1,\
                    linenum_to_title, distance_function, visited_node_ids)
    except KeyError:
        print "sr_id = %d, dst_id = %d, neighbors of src = %s" % (src_id, dst_id, str(adj_list_arg[src_id]))
        raise KeyError

# Wrapper for search()
def run_decentralized_search(src_id, dst_id, adj_list, linenum_to_title, distance_function):
    print "Running decentralized search..."
    try:
        return search(src_id, dst_id, adj_list, 0, linenum_to_title, distance_function, set())
    except KeyError:
        print "In run_decentralized_search(): KeyError in search()"
        return (None, None)
        
# The distance function to be used in search()
def distance(article_id1, article_id2):
    article1_name = linenum_to_title[str(article_id1)]
    article2_name = linenum_to_title[str(article_id2)]
    return get_article_distance(article1_name, article2_name)

