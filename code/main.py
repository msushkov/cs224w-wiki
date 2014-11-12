import random

import util
import load_data

# The list of all Wikipedia articles
articles = load_data.name_to_type.keys()

N = 100

# pick some number of random pairs of articles.
# for each pair, compute the distance given by decentralized search - that is the predicted distance
# for that same pair, also compute the distance using the ontology tree
for i in range(N):
	article1_name = random.choice(articles)
	article2_name = random.choice(articles)
	while article1_name == article2_name:
		article2_name = random.choice(articles)

	# predicted distance
	(success_or_fail, predicted_distance) = util.run_decentralized_search(article1_name, article2_name)

	# ontology distance
	ontology_distance = load_data.get_ontology_distance(article1_name, article2_name)

	print "Article 1: %s, Article 2: %s, Predicted distance = %d, Ontology distance = %d" % (article1_name, article2_name, predicted_distance, ontology_distance)

