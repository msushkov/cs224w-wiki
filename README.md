cs224w-wiki
===========

http://mappings.dbpedia.org/server/ontology/classes/

in order to do this, process the ontology tree file first and create a tree out of the links. create a function that omputes the height of a node in this tree (verify against the ontology UI)
once we have the tree we can compute the gold set: how far away nodes are from each other.
now, write a function taht does decentralized search on a given graph. load the graph into snappy and use a basic distance metric to compute distances between random pairs of nodes
