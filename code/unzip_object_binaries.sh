#! /bin/bash

#
# NOTE: this script must be executed from the directory where it lives
#

ADJ_LIST=adj_list.pk1
ARTICLE_NAMES=article_names.pk1
LINENUM_TO_TITLE=linenum_to_title.pk1
TITLE_TO_LINENUM=title_to_linenum.pk1
TYPE_TO_DEPTH=type_to_depth.pk1
NAME_TO_TYPE=name_to_type.pk1

cd bin

# if the unzipped files don't exist, unzip them

if [ ! -f "$ADJ_LIST" ]; then
    bunzip2 "$ADJ_LIST"
fi

if [ ! -f "$ARTICLE_NAMES" ]; then
    bunzip2 "$ARTICLE_NAMES"
fi

if [ ! -f "$LINENUM_TO_TITLE" ]; then
    bunzip2 "$LINENUM_TO_TITLE"
fi

if [ ! -f "$TITLE_TO_LINENUM" ]; then
    bunzip2 "$TITLE_TO_LINENUM"
fi

if [ ! -f "$TYPE_TO_DEPTH" ]; then
    bunzip2 "$TYPE_TO_DEPTH"
fi

if [ ! -f "$NAME_TO_TYPE" ]; then
    bunzip2 "$NAME_TO_TYPE"
fi

cd ..