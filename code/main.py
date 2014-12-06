import random
import util
import load_data

print "Starting main.py..."

# Load necessary data structures from file (those computed in load_data)

articles = load_data.load_object("bin/article_names.pk1")
name_to_type = load_data.load_object("bin/name_to_type.pk1")
title_to_linenum = load_data.load_object("bin/title_to_linenum.pk1")
linenum_to_title = load_data.load_object("bin/linenum_to_title.pk1")
adj_list = load_data.load_object("bin/adj_list.pk1")
type_to_depth = load_data.load_object("bin/type_to_depth.pk1")

print "Loaded objects from binary files."

# articles = load_data.get_articles()
# name_to_type = load_data.get_name_to_type()
# title_to_linenum = load_data.get_title_to_linenum()
# linenum_to_title = load_data.get_linenum_to_title()
# adj_list = load_data.get_adj_list()
# type_to_depth = load_data.get_type_to_depth()

#print "(main) Hash of adj_list: " + str(load_data.get_hash(adj_list))

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


check_adj_list()


#
# HELPER FUNCTIONS
#

# Get the height of a node in the ontology tree given its article name.
def get_height(article_name):
    try:
        curr_type = name_to_type[article_name]
        return type_to_depth[curr_type]
    except KeyError:
        print "ARTICLE: " + str(article_name)
        print "TYPE: " + str(name_to_type[article_name])
        print type_to_depth[curr_type]
        return None

# Get the path length through the lowest common ancestor in the ontology tree.
def get_ontology_distance(article1_name, article2_name):
    article1_height = get_height(article1_name)
    article2_height = get_height(article2_name)

    article1_type_node = type_to_node[name_to_type[article1_name]]
    article2_type_node = type_to_node[name_to_type[article2_name]]

    lca_height = get_height(lowest_common_ancestor(type_to_node["ROOT"], \
        article1_type_node, article2_type_node))

    return abs(float(lca_height) - article1_height) + \
        abs(float(lca_height) - article2_height)

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


#
# RUN THE EXPERIMENT
#
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

        src_id = int(title_to_linenum[article1_name])
        dst_id = int(title_to_linenum[article2_name])

        # predicted distance
        (success_or_fail, predicted_distance) = util.run_decentralized_search(src_id, dst_id, \
            adj_list, linenum_to_title, util.get_article_distance)

        if success_or_fail == None or success_or_fail == "FAILURE":
            if success_or_fail != None:
                print "%s. Article 1: %s, Article 2: %s" % \
                    (success_or_fail, article1_name, article2_name)
            else:
                print "KeyError..."
        else:
            num_success += 1

            # ontology distance
            ontology_distance = load_data.get_ontology_distance(article1_name, article2_name)

            print "%s. Article 1: %s, Article 2: %s, Predicted distance = %d, Ontology distance = %d" % \
                (success_or_fail, article1_name, article2_name, predicted_distance, ontology_distance)

#run_experiment()