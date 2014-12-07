#! /bin/bash

#
# NOTE: this script must be executed from the directory where it lives
#

echo "Catting data files..."

EDGES_FILE=links.txt
TITLES_FILE=titles.txt
INSTANCE_TYPES_FILE=instance_types.txt
ONTOLOGY_FILE=tree_links.txt

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

cd ..
export ONTOLOGY_FILE="$( pwd )/$(basename "$ONTOLOGY_FILE" )"

cd ../code
echo "Done."