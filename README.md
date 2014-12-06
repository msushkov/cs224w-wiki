cs224w-wiki
===========

# Setup

To create the binary data object files in code/bin (the ones used by the python scripts), run from the code directory:

$ source create_data.sh

and all the data files will be properly created. Running the script will also ensure that the proper environment variables are set (used by the python scripts).

This is only necessary if the data changes, or for some reason you wish to regenerate the object files. In most situations this step is unnecessary and you can work directly with the pk1 files in code/bin.

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