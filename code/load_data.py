import os
from collections import Counter
import numpy as np
import cPickle as pickle

# Get the absolute file paths
EDGES_FILE = os.environ['EDGES_FILE']
TITLES_FILE = os.environ['TITLES_FILE']
INSTANCE_TYPES_FILE = os.environ['INSTANCE_TYPES_FILE']
ONTOLOGY_FILE = os.environ['ONTOLOGY_FILE']

# Utility for saving an object to a file
def save_object(obj, filename):
    with open(filename, 'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

def load_object(filename):
    obj = None
    with open(filename, 'rb') as input1:
        obj = pickle.load(input1)
    return obj

class Node:
    def __init__(self, value):
        self.value = value
        self.children = set()

    def add_child(self, child_node):
        self.children.add(child_node)

    def get_children(self):
        return self.children

# mapping from type name to the corresponding node article
type_to_node = {}

# mapping from type name to its depth in the hierarchy
type_to_depth = {}

# Build the ontology tree
root = Node("ROOT")
type_to_node["ROOT"] = root

def process_ontology_file():
    print "Processing ontology file..."
    f = open(ONTOLOGY_FILE, 'r')
    for line in f:
        vals = line.strip().split()
        
        # the string names of the child and parent nodes
        node_val = vals[0]
        parent_val = vals[1]

        # the actual nodes
        curr_node = None
        curr_parent = None

        # get the node objects: either create new ones if they haven't been seen, or use the ones previously created

        if node_val not in type_to_node:
            curr_node = Node(node_val)
            type_to_node[node_val] = curr_node
        else:
            curr_node = type_to_node[node_val]

        # a Thing is a child of the root
        if parent_val == "2002/07/owl#Thing":
            curr_parent = type_to_node["ROOT"]
        else:
            if parent_val not in type_to_node:
                curr_parent = Node(parent_val)
                type_to_node[parent_val] = curr_parent
            else:
                curr_parent = type_to_node[parent_val]
        
        curr_parent.add_child(curr_node)

    f.close()
    print "Done processing ontology file."

# Populate the type_to_depth map.
def mark_depths(root, height):
    type_to_depth[root.value] = height
    for child in root.get_children():
        mark_depths(child, height + 1)

# mapping from name of article -> type in the hierarchy
name_to_type = {}

def process_instance_types_file():
    print "Processing instance types file..."
    # Load the instance types
    f2 = open(INSTANCE_TYPES_FILE, 'r')
    for line in f2:
        if line.strip().endswith("basketball_team:NCAATeamSeason,SportsTeamSeason,SportsSeason"):
            continue 

        vals = line.strip().split('\t')
        try:
            curr = vals[0]
            types = vals[1].split(',')

            if curr == "#":
                continue

            # find the type with the greatest depth; take the most specific type for each article
            max_depth = -1
            best_type = None
            for tpe in types:
                curr_type = tpe.strip()
                if curr_type in type_to_depth:
                    curr_depth = type_to_depth[curr_type]
                    if curr_depth > max_depth:
                        max_depth = curr_depth
                        best_type = curr_type

            name_to_type[curr] = best_type

        except:
            print "Line = " + line
            raise IndexError()

    f2.close()
    print "Done processing instance types file."

# Load the linenum -> article title map and the article title -> linenum

# string to string (both)
linenum_to_title = {}
title_to_linenum = {}

def process_titles_file():
    print "Processing titles file..."
    f1 = open(TITLES_FILE, 'r')
    count = 1
    for line in f1:
      line = line.strip()
      linenum_to_title[str(count)] = line
      title_to_linenum[line] = str(count)
      count += 1
    f1.close()
    print "Done processing titles file."

# need mapping between node id's in the edges file and the index into the adj matrix
edges_id_to_adj_index = {}

# inverse mapping of above
adj_index_to_edges_id = {}

# map of adj lists between indices
# int -> numpy array
adj_matrix = {}

def process_edges_file():
    print "Processing edges file..."
    c = 0
    total = 0
    n_edges = 0
    adj_matrix_id = 0
    f3 = open(EDGES_FILE, 'r')
    for line in f3:
        if total % 100000 == 0: print total

        total += 1
        vals = line.strip().split(':')
        src = vals[0].strip()
        dst_list = vals[1].strip().split()

        # make sure we have the source node in our instance types dataset
        src_name = linenum_to_title[src]
        if src_name in name_to_type:
            c += 1

            # get the index into the adj matrix for the source node
            src_adj_index = -1
            if src in edges_id_to_adj_index:
                src_adj_index = edges_id_to_adj_index[src]
            else:
                src_adj_index = adj_matrix_id
                edges_id_to_adj_index[src] = adj_matrix_id
                adj_matrix_id += 1

            adj_index_to_edges_id[adj_matrix_id] = src

            for dst in dst_list:
                # make sure the destination exists in all our datasets; otherwise just skip it
                dst_name = linenum_to_title[dst]
                if dst_name in name_to_type:
                    # get the index into the adj matrix for the destination node
                    dst_adj_index = -1
                    if dst in edges_id_to_adj_index:
                        dst_adj_index = edges_id_to_adj_index[dst]
                    else:
                        dst_adj_index = adj_matrix_id
                        edges_id_to_adj_index[dst] = adj_matrix_id
                        adj_matrix_id += 1

                    adj_index_to_edges_id[adj_matrix_id] = dst

                    # mark this edge in the adj matrix
                    #adj_matrix[(src_adj_index, dst_adj_index)] = 1
                    if src_adj_index in adj_matrix:
                        np.append(adj_matrix[src_adj_index], dst_adj_index)
                    else:
                        adj_matrix[src_adj_index] = np.array([dst_adj_index])

                    n_edges += 1

    f3.close()
    print "Done processing edges file."
    print "Number of nodes in Wiki dataset we have type information for = " + str(c)
    print "Number of edges = " + str(n_edges)
    print "Total number of nodes in Wikipedia dataset = " + str(total)


# append the string names to path
def get_path(root, node, path):
    path.append(root.value)

    if root.value != node.value:
        for child in root.get_children():
            get_path(child, node, path)
    else:
        return path

# Get the path from the root to both nodes; then find the point at which they start to diverge.
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

    lca_height = get_height(lowest_common_ancestor(type_to_node["ROOT"], article1_type_node, article2_type_node))

    return abs(float(lca_height) - article1_height) + abs(float(lca_height) - article2_height)

def convert_adj_ids_to_article_names(adj_matrix_id1, adj_matrix_id2):
    article1_linenum = adj_index_to_edges_id[adj_matrix_id1]
    article2_linenum = adj_index_to_edges_id[adj_matrix_id2]

    article1_name = linenum_to_title[article1_linenum]
    article2_name = linenum_to_title[article2_linenum]

    return (article1_name, article2_name)


def run_data_processing():
    process_ontology_file()
    mark_depths(type_to_node["ROOT"], 0)
    process_instance_types_file()
    process_titles_file()

    print "Number of Wikipedia articles (nodes) = " + str(len(name_to_type))
    print "Number of nodes in the hierarchy (not including ROOT) = " + str(len(type_to_depth) - 1)
    print "Max depth of hierarchy = " + str(max(type_to_depth.values()))
    
    process_edges_file()

    # save the objects that will be used by others into files
    save_object(name_to_type, "bin/name_to_type.pk1")
    save_object(title_to_linenum, "bin/title_to_linenum.pk1")
    save_object(edges_id_to_adj_index, "bin/edges_id_to_adj_index.pk1")
    save_object(adj_matrix, "bin/adj_matrix.pk1")

#run_data_processing()