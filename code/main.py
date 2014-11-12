import random

import util
import load_data

# The list of all Wikipedia articles
articles = load_data.load_object("bin/name_to_type.pk1").keys()

N = 5
num_success = 0

# pick some number of random pairs of articles.
# for each pair, compute the distance given by decentralized search - that is the predicted distance
# for that same pair, also compute the distance using the ontology tree
while num_success < N:
    article1_name = random.choice(articles)
    article2_name = random.choice(articles)
    while article1_name == article2_name:
        article2_name = random.choice(articles)

    # predicted distance
    (success_or_fail, predicted_distance) = util.run_decentralized_search(article1_name, article2_name)

    if success_or_fail == None or success_or_fail == "FAILURE":
        if success_or_fail != None:
            print "%s. Article 1: %s, Article 2: %s" % (article1_name, article2_name)
        else:
            print "KeyError..."
    else:
        num_success += 1

        # ontology distance
        ontology_distance = load_data.get_ontology_distance(article1_name, article2_name)

        print "%s. Article 1: %s, Article 2: %s, Predicted distance = %d, Ontology distance = %d" % (success_or_fail, article1_name, article2_name, predicted_distance, ontology_distance)
