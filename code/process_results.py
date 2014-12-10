import load_data
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np

gold_set = load_data.load_object("bin/results/goldset.pk1")
feat1 = load_data.load_object("bin/results/feat1.pk1")
feat2 = load_data.load_object("bin/results/feat2.pk1")
feat3 = load_data.load_object("bin/results/feat3.pk1")
rand = load_data.load_object("bin/results/random_dec_search_1ktrials.pk1")
largest_deg_1k = load_data.load_object("bin/results/neighbor_with_largest_degree_1000pairs.pk1")

# 0 successes
largest_deg_100 = load_data.load_object("bin/results/neighbor_with_largest_degree.pk1")

smallest_deg_1k = load_data.load_object("bin/results/neighbor_with_smallest_degree_1ktrials.pk1")

# 0 successes
smallest_deg_100 = load_data.load_object("bin/results/neighbor_with_smallest_degree.pk1")


# text feats 1-3: 100 random article pairs
# random: for each of 100 random pairs, 1000 trials
# graph heuristics: 1000 random article pairs
def get_avg_success_rate(results):
    total_suc = 0
    total_fail = 0
    for (a1_name, a2_name, suc, fail, path_lengths) in results:
        total_suc += suc
        total_fail += fail
    return float(total_suc) / (total_fail + total_suc)

def run_avg_success():
    print "avg success of text feat1 = %f" % get_avg_success_rate(feat1)
    print "avg success of text feat2 = %f" % get_avg_success_rate(feat2)
    print "avg success of text feat3 = %f" % get_avg_success_rate(feat3)
    print "avg success of rand = %f" % get_avg_success_rate(rand)
    print "avg success of graph smallest deg = %f" % get_avg_success_rate(smallest_deg_1k)
    print "avg success of graph largest deg = %f" % get_avg_success_rate(largest_deg_1k)

#run_avg_success()

# in: feat1, feat2, or feat3
def transform(results):
    c = Counter()
    for (a1_name, a2_name, suc, fail, path_lengths) in results:
        if len(path_lengths) > 0:
            c[(a1_name, a2_name)] = np.average(path_lengths)
    return c

def plot1():
    tr_feat1 = transform(feat1)
    tr_feat2 = transform(feat2)
    tr_feat3 = transform(feat3)

    y1 = []
    y2 = []
    y3 = []
    y_lca = []
    y_ontdist = []
    y_shortest = []

    for (article1_name, article2_name, shortest_path_length, ont_dist, lca_height) in gold_set:
        y_lca.append(lca_height)
        y_ontdist.append(ont_dist)
        y_shortest.append(shortest_path_length)

        key = (article1_name, article2_name)

        y1.append(tr_feat1[key])
        y2.append(tr_feat2[key])
        y3.append(tr_feat3[key])   


    x = range(1, len(gold_set) + 1)

    plt.figure(1)
    plt.xlabel('Trial')
    plt.ylabel('Distance between articles in a given pair (trial)')
    plt.title('Results of decentralized search vs gold-set metrics, for 100 random article pairs (trials).')
    plt.plot(x, y1, 'ro-', label='Heuristic 1')
    plt.plot(x, y2, 'bo-', label='Heuristic 2')
    plt.plot(x, y3, 'go-', label='Heuristic 3')
    plt.plot(x, y_lca, 'ko-', label='Height of LCA')
    plt.legend(loc=2)
    plt.show()

def plot2():
    tr_feat1 = transform(feat1)
    tr_feat2 = transform(feat2)
    tr_feat3 = transform(feat3)

    y1 = []
    y2 = []
    y3 = []
    y_lca = []
    y_ontdist = []
    y_shortest = []

    for (article1_name, article2_name, shortest_path_length, ont_dist, lca_height) in gold_set:
        y_lca.append(lca_height)
        y_ontdist.append(ont_dist)
        y_shortest.append(shortest_path_length)

        key = (article1_name, article2_name)

        y1.append(tr_feat1[key])
        y2.append(tr_feat2[key])
        y3.append(tr_feat3[key])   


    x = range(1, len(gold_set) + 1)

    plt.figure(1)
    plt.xlabel('Trial')
    plt.ylabel('Distance between articles in a given pair (trial)')
    plt.title('Results of decentralized search vs gold-set metrics, for 100 random article pairs (trials).')
    plt.plot(x, y1, 'ro-', label='Heuristic 1')
    plt.plot(x, y2, 'bo-', label='Heuristic 2')
    plt.plot(x, y3, 'go-', label='Heuristic 3')
    plt.plot(x, y_ontdist, 'ko-', label='Ontology distance')
    plt.legend(loc=2)
    plt.show()

def plot3():
    tr_feat1 = transform(feat1)
    tr_feat2 = transform(feat2)
    tr_feat3 = transform(feat3)

    y1 = []
    y2 = []
    y3 = []
    y_lca = []
    y_ontdist = []
    y_shortest = []

    for (article1_name, article2_name, shortest_path_length, ont_dist, lca_height) in gold_set:
        y_lca.append(lca_height)
        y_ontdist.append(ont_dist)
        y_shortest.append(shortest_path_length)

        key = (article1_name, article2_name)

        y1.append(tr_feat1[key])
        y2.append(tr_feat2[key])
        y3.append(tr_feat3[key])   


    x = range(1, len(gold_set) + 1)

    plt.figure(1)
    plt.xlabel('Trial')
    plt.ylabel('Distance between articles in a given pair (trial)')
    plt.title('Results of decentralized search vs gold-set metrics, for 100 random article pairs (trials).')
    plt.plot(x, y1, 'ro-', label='Heuristic 1')
    plt.plot(x, y2, 'bo-', label='Heuristic 2')
    plt.plot(x, y3, 'go-', label='Heuristic 3')
    plt.plot(x, y_shortest, 'ko-', label='Actual shortest path')
    plt.legend(loc=2)
    plt.show()

plot3()