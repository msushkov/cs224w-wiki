import os
from collections import Counter
import numpy as np
import cPickle as pickle
import random
import hashlib

# Get the absolute file paths
EDGES_FILE = os.environ['EDGES_FILE']
TITLES_FILE = os.environ['TITLES_FILE']
INSTANCE_TYPES_FILE = os.environ['INSTANCE_TYPES_FILE']
ONTOLOGY_FILE = os.environ['ONTOLOGY_FILE']


# Utility for saving an object to a file
def save_object(obj, filename):
    with open(filename, 'wb') as output:
        pickle.dump(obj, output, -1)

def load_object(filename):
    obj = None
    with open(filename, 'rb') as input1:
        obj = pickle.load(input1)
    return obj

# Nodes in the ontology tree
class Node:
    def __init__(self, value):
        self.value = value
        self.children = set()

    def add_child(self, child_node):
        self.children.add(child_node)

    def get_children(self):
        return self.children

    def __str__(self):
        return self.value


# mapping from type name to the corresponding node article
type_to_node = {}

# Build the ontology tree
root = Node("ROOT")
type_to_node["ROOT"] = root


'''
Goes through the ontology file and creates the ontology tree in memory: populates
the type_to_node dictionary.

Ontology file (node parent):
    BasketballLeague SportsLeague
    NaturalEvent Event
    Province GovernmentalAdministrativeRegion
    ...
'''
def process_ontology_file():
    global type_to_node

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


# Debug method for process_ontology_file().
# Prints to the console: node: child1 child2 ...
def print_ontology(curr_node):
    curr_line = curr_node.value
    curr_line += ": "

    children = curr_node.get_children()
    children_vals = []
    for child in children:
        children_vals.append(child.value)
    curr_line += " ".join(sorted(children_vals))

    print curr_line
    for child in children:
        print_ontology(child)


# mapping from type name to its depth in the hierarchy
type_to_depth = {}


# Populate the type_to_depth map.
def mark_depths(root, height):
    global type_to_depth

    type_to_depth[root.value] = height
    for child in root.get_children():
        mark_depths(child, height + 1)

# Debug method for mark_depths().
def print_depths(root, type_to_depth):
    for key in type_to_depth:
        print key + " " + str(type_to_depth[key])


# mapping from name of article -> type in the hierarchy
name_to_type = {}


'''
Go through the instance types file and populate name_to_type. Keys are names 
of Wikipedia articles; values are types (keys into type_to_node and type_to_depth).

Instance types file (4,219,549 lines):
    Autism  Disease
    Aristotle   Philosopher, Person
    Alabama AdministrativeRegion, Region, PopulatedPlace, Wikidata:Q532, Place
    ...
'''
def process_instance_types_file():
    global name_to_type

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

            # skip commented lines; skip things that are secondary or tertiary
            # (e.g. Sergio_Molina_Rivero__1 as opposed to Sergio_Molina_Rivero)
            if curr == "#" or curr[-3:-1] == "__":
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

# Debug method for process_instance_types_file(). Prints some number of article types at random.
def print_instance_types(num_to_print):
    keys = name_to_type.keys()
    random.shuffle(keys)
    rand_keys = keys[:num_to_print]
    for key in rand_keys:
        print key + ": " + name_to_type[key]


# Load the linenum -> article title map and the article title -> linenum

# string to string (both)
linenum_to_title = {}
title_to_linenum = {}

def process_titles_file():
    global linenum_to_title, title_to_linenum

    print "Processing titles file..."
    f1 = open(TITLES_FILE, 'r')
    count = 1
    for line in f1:
      line = line.strip()
      if line[-3:-1] == "__":
        continue
      linenum_to_title[str(count)] = line
      title_to_linenum[line] = str(count)
      count += 1
    f1.close()
    print "Done processing titles file."


# Adj list of article id to list of article ids that are connected to that article 
# int -> numpy array
adj_list = {}

# Edges file has 5706070 lines.
def process_edges_file():
    global adj_list

    print "Processing edges file..."
    c = 0
    total = 0
    n_edges = 0
    f3 = open(EDGES_FILE, 'r')
    for line in f3:
        #if total == 500000: break

        # print progress as a percentage (only 1 decimal place)
        if total % 500000 == 0:
            print str("{0:.1f}".format(total / 5706070.0 * 100.0)) + "% done reading edges file"

        total += 1
        vals = line.strip().split(':')
        src = vals[0].strip()
        dst_list = vals[1].strip().split()

        src_name = linenum_to_title[src]
        if src_name in article_names:
            c += 1
            num_src = np.uint32(src)

            for dst in dst_list:
                # make sure the destination exists in all our datasets; otherwise just skip it
                dst_name = linenum_to_title[dst.strip()]
                if dst_name in article_names:
                    num_dst = np.uint32(dst.strip())

                    # mark this edge in the adj matrix
                    if num_src not in adj_list:
                        adj_list[num_src] = np.array([], dtype=np.uint32)
                    adj_list[num_src] = np.append(adj_list[num_src], num_dst)

                    if num_src < 1 or num_src > 5706070 or num_dst < 1 or num_dst > 5706070:
                        print "OUT OF RANGE!!!"

                    n_edges += 1

    f3.close()
    print "Done processing edges file."
    print "Number of nodes in Wiki dataset we have type information for = " + str(c)
    print "Number of edges = " + str(n_edges)
    print "Total number of nodes in Wikipedia dataset = " + str(total)


def get_articles():
    return list(article_names)
def get_name_to_type():
    return name_to_type
def get_title_to_linenum():
    return title_to_linenum
def get_linenum_to_title():
    return linenum_to_title
def get_adj_list():
    return adj_list
def get_type_to_depth():
    return type_to_depth


# Set of Wiki article names (for which we have complete information)
article_names = None

# Main function
def run_data_processing():
    global article_names

    process_ontology_file()
    mark_depths(type_to_node["ROOT"], 0)

    process_instance_types_file()
    process_titles_file()

    print "Number of Wikipedia articles (nodes) = " + str(len(name_to_type))
    print "Number of nodes in the hierarchy (not including ROOT) = " + str(len(type_to_depth) - 1)
    print "Max depth of hierarchy = " + str(max(type_to_depth.values()))
    
    # We have 2 data sources: one has one set of article names (the instance types data), and
    # the other has another set of article names (the Wiki edgelist data).
    # Now we need to compute the intersection of these 2 sets of article names to get a set of
    # article names for which we have both type information and Wiki graph information.
    article_names = set(name_to_type.keys()).intersection(set(title_to_linenum.keys()))
    print "Number of actual article names: " + str(len(article_names))

    process_edges_file()

    # save the objects that will be used by others into files
    save_object(list(article_names), "bin/article_names.pk1")
    save_object(name_to_type, "bin/name_to_type.pk1")
    save_object(title_to_linenum, "bin/title_to_linenum.pk1")
    save_object(linenum_to_title, "bin/linenum_to_title.pk1")
    save_object(adj_list, "bin/adj_list.pk1")
    save_object(type_to_depth, "bin/type_to_depth.pk1")

#run_data_processing()

def save_type_to_node():
    process_ontology_file()
    save_object(type_to_node, "bin/type_to_node.pk1")