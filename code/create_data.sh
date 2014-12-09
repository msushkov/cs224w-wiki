#! /bin/bash

#
# NOTE: this script must be executed from the directory where it lives
#

echo "Catting data files..."

EDGES_FILE=links.txt
TITLES_FILE=titles.txt
INSTANCE_TYPES_FILE=instance_types.txt
ONTOLOGY_FILE=tree_links.txt
WIKI_FILE=articles.txt
INDEX_FILE=index.txt
DICTIONARY_FILE=dictionary.txt
CORPUS_FILE=corpus.txt
LDA_FILE=lda.txt
TFIDF_FILE=tfidf.txt

cd ../data

export STOP_WORDS_FILE="$( pwd )/$(basename "english_stopwords.txt" )"

cd edges

# if we already catted the file, don't do anything
if [ ! -f "$EDGES_FILE" ]; then 
	cat links_1.txt links_2.txt links_3.txt links_4.txt links_5.txt links_6.txt links_7.txt links_8.txt links_9.txt links_10.txt links_11.txt > $EDGES_FILE
fi

# if we already catted the file, don't do anything
if [ ! -f "$TITLES_FILE" ]; then 
	cat titles_sorted_1.txt titles_sorted_2.txt > $TITLES_FILE
fi

cd ../instance_types

# if we already catted the file, don't do anything
if [ ! -f "$INSTANCE_TYPES_FILE" ]; then
	cat instance_types_1.txt instance_types_2.txt instance_types_3.txt > $INSTANCE_TYPES_FILE
fi

export INSTANCE_TYPES_FILE="$( cd "$(dirname "$INSTANCE_TYPES_FILE")" && pwd)/$(basename "$INSTANCE_TYPES_FILE" )"

cd ../edges

export EDGES_FILE="$( cd "$(dirname "$EDGES_FILE")" && pwd)/$(basename "$EDGES_FILE" )"
export TITLES_FILE="$( cd "$(dirname "$TITLES_FILE")" && pwd)/$(basename "$TITLES_FILE" )"

cd ../wiki_index

export WIKI_FILE="$( cd "$(dirname "$WIKI_FILE")" && pwd)/$(basename "$WIKI_FILE" )"
export INDEX_FILE="$( cd "$(dirname "$INDEX_FILE")" && pwd)/$(basename "$INDEX_FILE" )"

cd ../lda

export DICTIONARY_FILE="$( cd "$(dirname "$DICTIONARY_FILE")" && pwd)/$(basename "$DICTIONARY_FILE" )"
export CORPUS_FILE="$( cd "$(dirname "$CORPUS_FILE")" && pwd)/$(basename "$CORPUS_FILE" )"
export LDA_FILE_10="$( pwd )/10/$(basename "$LDA_FILE" )"
export LDA_FILE_30="$( pwd )/30/$(basename "$LDA_FILE" )"
export LDA_FILE_60="$( pwd )/60/$(basename "$LDA_FILE" )"
export LDA_FILE_120="$( pwd )/120/$(basename "$LDA_FILE" )"

cd ../tfidf

export TFIDF_FILE="$( cd "$(dirname "$TFIDF_FILE")" && pwd)/$(basename "$TFIDF_FILE" )"

cd ../snap
export GRAPH_OBJECT_FILE="$( pwd )/max_scc.txt"

cd ..
export ONTOLOGY_FILE="$( pwd )/$(basename "$ONTOLOGY_FILE" )"

cd ../code/bin

export ARTICLE_NAMES_30K="$( pwd )/article_names_30k.pk1"
export ADJ_LIST_30K="$( pwd )/adj_list_30k.pk1"
export ARTICLE_PAIRS="$( pwd )/article_pairs.pk1"

cd ..
echo "Done."
