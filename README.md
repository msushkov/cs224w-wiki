cs224w-wiki
===========

# Setup

To create the binary data object files in code/bin (the ones used by the python scripts), run from the code directory:

$ source create_data.sh

and all the data files will be properly created. Running the script will also ensure that the proper environment variables are set (used by the python scripts).

In order to use the object files in code/bin, run from the code directory:

$ source unzip_object_binaries.sh

Now you are ready to easily load the data into memory and use it to run experiments.


# Details

A visual representation of the ontology:
http://mappings.dbpedia.org/server/ontology/classes/


# TODOs

- cache article text
- featurize article pairs
- LDA
- ML infrastructure