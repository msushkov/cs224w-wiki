import linecache
from gensim.corpora.wikicorpus import process_article, tokenize
import util
import os.path

ARTICLES_FILE = os.environ['WIKI_FILE']
INDEX_FILE = os.environ['INDEX_FILE']


# Combines all articles into one file. One per line
def download_articles(article_names):
    with open(ARTICLES_FILE, 'w') as articles_file:
        with open(INDEX_FILE, 'w') as index_file:
            for article_name in article_names:
                print "Processing {0}".format(article_name)
                try:
                    text = util.get_article_text(article_name)
                    tokenized_article = tokenize(text)
                    tokenized_article = [w for w in tokenized_article if not w in util.STOP_WORDS]
                    for token in tokenized_article:
                        articles_file.write("{0} ".format(token))
                    articles_file.write("\n")
                    index_file.write("{0}\n".format(article_name))

                except util.ArticleNotFoundError:
                    print "Could not find: {0}".format(article_name)
                except:
                    print "Error getting article"


def get_article(article_name, article_name_to_linenum):
    return linecache.getline(ARTICLES_FILE, article_name_to_linenum[article_name])

def get_article_name_to_linenum():
    article_name_to_linenum = {}

    # load index
    with open(INDEX_FILE, "r") as index:
        line_num = 1
        for line in index:
            article_name_to_linenum[line.strip()] = line_num
            line_num += 1
    return article_name_to_linenum


# download articles
if not os.path.isfile(INDEX_FILE) or not os.path.isfile(ARTICLES_FILE):
    download_articles(["Metropolitan_area", "Washington_metropolitan_area", "The_Hunger_Games", "Stanford_University", "Washington,_D.C.", "Washington_Redskins", "asdfasdgasfg"])

#print get_article("Washington_Redskins", get_article_name_to_linenum())
#print get_article("Washington,_D.C.")

