import random
import util
import load_data
import snap
import numpy as np
import os
import wiki_index
import ml
import copy

print "Starting main.py..."

ARTICLE_NAMES_30K_FILE = os.environ['ARTICLE_NAMES_30K']
ADJ_LIST_30K_FILE = os.environ['ADJ_LIST_30K']
ARTICLE_PAIRS_FILE = os.environ['ARTICLE_PAIRS']
GRAPH_OBJECT_FILE = os.environ['GRAPH_OBJECT_FILE']

# Load necessary data structures from file (those computed in load_data)

articles = load_data.load_object("bin/article_names.pk1")
name_to_type = load_data.load_object("bin/name_to_type.pk1")
title_to_linenum = load_data.load_object("bin/title_to_linenum.pk1")
linenum_to_title = load_data.load_object("bin/linenum_to_title.pk1")
adj_list = load_data.load_object("bin/adj_list.pk1")
type_to_depth = load_data.load_object("bin/type_to_depth.pk1")
type_to_node = load_data.load_object("bin/type_to_node.pk1")

print "Loaded objects from binary files."


# Debug: look at adj_list length distribution
def print_adj_list_lengths(k):
    vals = adj_list.values()
    lengths = []
    for v in vals:
        l = len(v)
        lengths.append(l)
    random.shuffle(lengths)
    print lengths[:k]

# Debug: make sure each element in adj_matrix is between 1 and 5706070.
def check_adj_list():
    vals = []

    # check keys
    for elem in adj_list.keys():        
        if check_val(elem):
            pass
        else:
            print "adj_list has keys that are out of range!!! " + str(elem)
            break

        for x in adj_list[elem]:
            if check_val(x):
                pass
            else:
                print "adj_list has values that are out of range!!! " + str(elem)
                break

    print "Done checking adj_list."
    
def check_val(value):
    return value >= 1 and value <= 5706070


#
# HELPER FUNCTIONS
#

# Get the height of a node in the ontology tree given its article name.
def get_height(article_name):
    try:
        curr_type = name_to_type[article_name]
        return type_to_depth[curr_type]
    except KeyError:
        print "KeyError in get_height(). ARTICLE: %s, TYPE: %s" % (str(article_name), str(name_to_type[article_name]))
        raise KeyError

# Get the path length through the lowest common ancestor in the ontology tree.
# Returns a tuple of (article1_height, article2_height, lca_height)
def get_ontology_distance(article1_name, article2_name):
    article1_height = get_height(article1_name)
    article2_height = get_height(article2_name)

    article1_type = name_to_type[article1_name]
    article2_type = name_to_type[article2_name]

    #print "article 1: name = %s, type = %s, height = %d; article 2: name = %s, type = %s, height = %d" % \
    #    (article1_name, article1_type, article1_height, article2_name, article2_type, article2_height)

    article1_type_node = type_to_node[article1_type]
    article2_type_node = type_to_node[article2_type]

    root_node = type_to_node["ROOT"]
    lca = lowest_common_ancestor(root_node, article1_type_node, article2_type_node)
    lca_height = type_to_depth[lca]

    return (abs(float(lca_height) - article1_height) + \
        abs(float(lca_height) - article2_height), lca_height)
    #return (article1_height, article2_height, lca_height)

# append the string names to path
def get_path(root, node, path):
    new_path = copy.deepcopy(path)
    new_path.append(root.value)

    if root.value != node.value:
        for child in root.get_children():
            p = get_path(child, node, new_path)
            if p != None:
                return p
        return None
    else:
        return new_path

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
    return last_equal

#
# GRAPH PROCESSING
#

# Load the graph into snap, find largest SCC, update articles and adj_list to only
# contain nodes in that SCC. Then save the article names, adj_list, and the graph object to
# binary files.
def process_in_snappy():
    global articles, adj_list

    print "Starting graph processing..."

    G1 = create_snap_graph_from_adjlist(adj_list)

    print "Finding largest CC..."

    G = snap.GetMxScc(G1)

    print "Size of max SCC (nodes): %s" % str(G.GetNodes())
    print "Size of max SCC (edges): %s" % str(G.GetEdges())

    # update articles
    print "Updating articles..."
    new_articles = []
    for node in G.Nodes():
        node_id = node.GetId()
        article_name = linenum_to_title[str(node_id)]
        new_articles.append(article_name)

    print "Length of new articles = %d" % len(new_articles)

    # update adj_list
    print "Updating adj_list..."
    new_adj_list = {}
    for Edge in G.Edges():
        src_id = Edge.GetSrcNId()
        dst_id = Edge.GetDstNId()
    
        num_src = np.uint32(src_id)
        num_dst = np.uint32(dst_id)

        if num_src not in new_adj_list:
            new_adj_list[num_src] = np.array([], dtype=np.uint32)
        new_adj_list[num_src] = np.append(new_adj_list[num_src], num_dst)

    # save adj_list and articles
    print "Saving to binary..."
    articles = new_articles
    adj_list = new_adj_list
    load_data.save_object(new_adj_list, "bin/adj_list.pk1")
    load_data.save_object(new_articles, "bin/article_names.pk1")


def create_snap_graph_from_adjlist(adj_list_arg):
    G1 = snap.TNGraph.New()
    c = 0
    for src in adj_list_arg:
        c += 1
        if c % 10000 == 0:
            print "Finished %d..." % c

        if not G1.IsNode(int(src)):
            G1.AddNode(int(src))

        for dst in adj_list_arg[src]:
            if not G1.IsNode(int(dst)):
                G1.AddNode(int(dst))
            G1.AddEdge(int(src), int(dst))
    return G1

def get_graph_shortest_path(G, node1_id, node2_id):
    return snap.GetShortPath(G, node1_id, node2_id, True)


# Input: the graph object that is the max SCC of the wiki graph
# Returns: a graph that is a subgraph of size 30k of the input graph
def save_30k_articles(G):
    NUM = 30000
    articles_30k = set()
    ids_30k = set()
    curr_hop = 1
    
    first_article = random.choice(articles)
    first_id = int(title_to_linenum[first_article])
    articles_30k.add(first_article)
    ids_30k.add(first_id)

    while len(articles_30k) < NUM:
        NodeVec = snap.TIntV()
        snap.GetNodesAtHop(G, first_id, curr_hop, NodeVec, True)
        for next_id in NodeVec:
            title = linenum_to_title[str(next_id)]
            articles_30k.add(title)
            ids_30k.add(next_id)
        curr_hop += 1

    print "It took %d hops to get to %d nodes!" % (curr_hop, NUM)

    load_data.save_object(list(articles_30k), ARTICLE_NAMES_30K_FILE)

    # save adj_list_30k
    new_adj_list = {}

    for key in adj_list.keys():
        if key in ids_30k:
            if key not in new_adj_list:
                new_adj_list[key] = np.array([], dtype=np.uint32)

            for node_id in adj_list[key]:
                if node_id in ids_30k:
                    new_adj_list[key] = np.append(new_adj_list[key], node_id)

    load_data.save_object(new_adj_list, ADJ_LIST_30K_FILE)


# Returns a list of 30k article names.
def load_30k_articles():
    return load_data.load_object(ARTICLE_NAMES_30K_FILE)

# Returns an adjacency list dictionary.
def load_30k_adj_list():
    return load_data.load_object(ADJ_LIST_30K_FILE)

def load_30k_graph_object():
    return snap.LoadEdgeList(snap.PNGraph, GRAPH_OBJECT_FILE, 0, 1)

def save_30k_graph_object():
    G = create_snap_graph_from_adjlist(load_30k_adj_list())
    snap.SaveEdgeList(G, GRAPH_OBJECT_FILE)

def build_index():
    wiki_index.build_indexes(load_30k_articles())


def save_article_pairs():
    NUM_PAIRS = 50000

    articles_30k = load_30k_articles()
    article_pairs = [] # list of (name1, name2)

    count = 0
    while count < NUM_PAIRS:
        article1_name = random.choice(articles_30k)
        article2_name = random.choice(articles_30k)
        while article1_name == article2_name:
            article2_name = random.choice(articles_30k)
        article_pairs.append((article1_name, article2_name))
        count += 1

    load_data.save_object(article_pairs, ARTICLE_PAIRS_FILE)

def load_article_pairs():
    return load_data.load_object(ARTICLE_PAIRS_FILE)

def save_pairwise_distances(actual_shortest_path):
    load_data.save_object(actual_shortest_path, "bin/pairwise_distances.pk1")

def load_pairwise_distances():
    return load_data.load_object("bin/pairwise_distances.pk1")

#
# RUN THE EXPERIMENT
#

# runs decentralized search
def run_experiment():
    N = 5
    num_success = 0

    # pick some number of random pairs of articles.
    # for each pair, compute the dist given by decentralized search: that's the predicted dist
    # for that same pair, also compute the distance using the ontology tree
    while num_success < N:
        article1_name = random.choice(articles)
        article2_name = random.choice(articles)
        while article1_name == article2_name:
            article2_name = random.choice(articles)

        print "Article 1: %s, article 2: %s" % (article1_name, article2_name)

        src_id = int(title_to_linenum[article1_name])
        dst_id = int(title_to_linenum[article2_name])

        # predicted distance
        (success_or_fail, predicted_distance) = util.run_decentralized_search(src_id, dst_id, \
            adj_list, linenum_to_title, util.get_article_distance)

        # failure or error
        if success_or_fail == None or success_or_fail == "FAILURE":
            if success_or_fail != None:
                print "%s. Article 1: %s, Article 2: %s" % \
                    (success_or_fail, article1_name, article2_name)
            else:
                print "KeyError..."
        # success
        else:
            num_success += 1

            # ontology distance
            ontology_distance = get_ontology_distance(article1_name, article2_name)

            print "%s. Article 1: %s, Article 2: %s, Predicted distance = %d, Ontology distance = %d" % \
                (success_or_fail, article1_name, article2_name, predicted_distance, ontology_distance)


# Tries to learn the shortest path as a function of the features.
def run_ml_on_distances():
    count = 0
    #num_lda_topics_list = [10, 30, 60]
    num_lda_topics_list = [10]

    # holds tuples of (article1_name, article2_name, shortest_path)
    actual_shortest_path = []

    # holds tuples of (article1_name, article2_name, [feat1, feat2, ...])
    nlp_features = []
    
    G = load_30k_graph_object()
    #bigG = create_snap_graph_from_adjlist(adj_list)
    article_pairs = load_article_pairs()

    print "There are %d article pairs." % len(article_pairs)

    for num_lda_topics in num_lda_topics_list:
        for (article1_name, article2_name) in article_pairs[:1000]:
            if count % 100 == 0:
                print count

            #print "Article 1: %s, article 2: %s" % (article1_name, article2_name)

            try:
                src_id = int(title_to_linenum[article1_name])
                dst_id = int(title_to_linenum[article2_name])

                #path_length = get_graph_shortest_path(G, src_id, dst_id)
                (path_length, lca_height) = get_ontology_distance(article1_name, article2_name)
                print (path_length, lca_height)
                
                features = util.extract_nlp_features(article1_name, article2_name, num_lda_topics, name_to_type, type_to_depth, type_to_node)

                curr_actual = (article1_name, article2_name, lca_height)
                curr_feat = (article1_name, article2_name, features)

                actual_shortest_path.append(curr_actual)
                nlp_features.append(curr_feat)

                count += 1
            
            except KeyError:
                continue

        #save_pairwise_distances(actual_shortest_path)

        #print "Number of article pairs actually analyzed: %d" % len(nlp_features)

        # now we have the actual distances and the features. do regression on them.
        # error will be MSE on the distance
        score = ml.run_ml(nlp_features, actual_shortest_path, True)

        print "Num LDA topics = %d" % num_lda_topics
        print score


run_ml_on_distances()
