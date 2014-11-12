import urllib2
import json
import nltk
from HTMLParser import HTMLParser
import string

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
	
	return result

# Return list of nodes for which adj_matrix[v, w] > 0
def get_neighbors(v, adj_matrix_arg):
	nbrs = []
	for i, val in enumerate(adj_matrix_arg[v]):
		if val > 0:
			nbrs.append(i)
	return nbrs

# Runs decentralized search
# source and destination are indices into adj_matrix_arg
# similarity_function takes in 2 indices (in adj_matrix_arg) of nodes and returns a floating-point distance between them
def search(source, destination, adj_matrix_arg, path_length, distance_function):
    neighbors = get_neighbors(source, adj_matrix_arg)

    # pick the best neighbor of source (the one that has the smallest distance to destination, given by distance_function)
    best_neighbor = None
    smallest_distance = float('inf')
    for node in neighbors:
        curr_distance_to_dest = distance_function(node, destination)
        if curr_distance_to_dest < smallest_distance:
            best_neighbor = node
            smallest_distance = curr_distance_to_dest
    if best_neighbor == destination:
        return ("SUCCESS", path_length + 1)
    else:
    	if path_length >= SEARCH_DIST_THRESHOLD:
    		return ("FAILURE", path_length + 1)
    	else:
    		return search(best_neighbor, destination, adj_matrix_arg, path_length + 1, distance_function)

    