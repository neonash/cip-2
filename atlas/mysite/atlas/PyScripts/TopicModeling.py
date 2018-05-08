path="C:/Users/akshat.gupta/Downloads/amazon-reviews-analysis-master/amazon-reviews-analysis-master/data/"
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
#import json
#import gzip
import logging
import re
import cPickle
import pyLDAvis.gensim
#from os.path import isfile
from sklearn.feature_extraction.text import CountVectorizer
from gensim.corpora import Dictionary
from gensim.models.lsimodel import LsiModel
from gensim.models.ldamodel import LdaModel
from gensim.models.tfidfmodel import TfidfModel
import pandas as pd
import traceback
from atlas.config import dbConfig


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', \
                    level=logging.INFO)


def id2word(dictionary):
    id2word = {}
    for word in dictionary.token2id:
        id2word[dictionary.token2id[word]] = word
    return id2word


def train_lda_model(corpus, dictionary, num_topics):
    lda = LdaModel(corpus=corpus, num_topics=num_topics, id2word=id2word(dictionary), \
                    alpha=0.2, update_every=5, chunksize=10000, passes=10, iterations=50)
    return lda


def train_lsi_model(corpus, dictionary):
    lsi = LsiModel(corpus=corpus, id2word=id2word(dictionary), num_topics=20, chunksize=10000,\
                   onepass=True)
    return lsi


def get_tokeniser(ngram_range=(1, 1), stop_words='english'):
    vect = CountVectorizer(ngram_range=ngram_range, stop_words=stop_words,max_df=0.8, max_features=5000,
                                   min_df=0.2)
    return vect.build_analyzer()


def prettify(topics):
    return map(lambda ts: re.sub("\\s\+", ",", ts), map(lambda t: re.sub("(\d*\.\d*\*)", "", t), topics))


def save(data, file):
    fo = open(file, 'wb')
    cPickle.dump(data, fo, protocol=2)
    fo.close()


def load(file):
    fo = open(file, 'rb')
    data = cPickle.load(fo)
    fo.close()
    return data


def valid(chunks, product):
    for chunk in chunks:
        mask = (chunk['pCategory'] == product)
        if mask.all():
            yield chunk
            print chunk
        else:
            yield chunk.loc[mask]
            print chunk.loc[mask]
            break


def main(request, num_topics):
    is_csv = 0
    if ".csv" in request:
        request = request[:-4]
        is_csv = 1
    #print(request)

    dataset_name = request
    tfidf_corpus_path = dbConfig.dict['topicModels'] + '%s_tfidf_corpus.pkl' % dataset_name
    tfidf_corpus = None
    #logging.info("inside main")

    #Reading only required rows
    status_code = 200
    #if not isfile(tfidf_corpus_path):
    try:
        if True:
            #logging.warn("No saved models available. Generating corpus. This might take a while...")
            print("No saved models available. Generating corpus. This might take a while...")
            #logging.info("Loading data from text file")
            if is_csv == 0:
                filename = dbConfig.dict['outputUrl']
                chunksize = 10 ** 5
                chunks = pd.read_csv(filename, chunksize=chunksize)
                df = pd.concat(valid(chunks, request))
            else:
                filename = dbConfig.dict['uploadsUrl'] + request + ".csv"
                df = pd.read_csv(filename)

            #print(df)

            #lines = open(r'C:/Users/akshat.gupta/Downloads/amazon-reviews-analysis-master/amazon-reviews-analysis-master/data/data.csv').readlines()
            lines = df['rText'].tolist()

            #logging.info("Tokenising data")
            tokeniser = get_tokeniser()
            texts = map(lambda s: tokeniser(s), lines)

            #logging.info("Saving corpus texts")
            #save(texts, 'data/models/%s_texts.pkl' % dataset_name)
            save(texts, dbConfig.dict['topicModels'] + '%s_texts.pkl' % dataset_name)


            #logging.info("Generating bag of words")
            dictionary = Dictionary(texts)
            #save(dictionary, 'data/models/%s_dict.pkl' % dataset_name)
            save(texts, dbConfig.dict['topicModels'] + '%s_dict.pkl' % dataset_name)

            corpus = [dictionary.doc2bow(text) for text in texts]

            #logging.info("Saving bag of words")
            #save(corpus, 'data/models/%s_corpus.pkl' % dataset_name)
            save(texts, dbConfig.dict['topicModels'] + '%s_corpus.pkl' % dataset_name)


            #logging.info("Applying Tfidf model to corpus")
            tfidf = TfidfModel(corpus)
            tfidf_corpus = [tfidf[c] for c in corpus]

            #logging.info("Saving TF-IDF transformed corpus")
            save(tfidf_corpus, tfidf_corpus_path)
            #pyLDAvis.enable_notebook()


        else:
            #logging.info("Loading saved TF-IDF dictionary")
            dictionary = load(dbConfig.dict['topicModels'] + '%s_dict.pkl' % dataset_name)
            #corpus = load('C:/Users/akshat.gupta/Downloads/amazon-reviews-analysis-master/amazon-reviews-analysis-master/data/models/%s_corpus.pkl' % dataset_name)
            #logging.info("Loading saved TF-IDF corpus")
            tfidf_corpus = load(tfidf_corpus_path)


        # #logging.info("Training LSI model")
        # lsi = train_lsi_model(tfidf_corpus, dictionary)
        # lsi_topics = prettify(lsi.show_topics(-1))
        # lsi_topic_distribution = [l for l in lsi[tfidf_corpus]]

        #logging.info("Training LDA model")
        lda = train_lda_model(tfidf_corpus, dictionary, num_topics)

        p = pyLDAvis.gensim.prepare(lda, tfidf_corpus, dictionary)
        kw = str(request).split(".")[0]
        print(kw)
        pyLDAvis.save_html(p, dbConfig.dict['topicViz'] + kw + ".html")
        #lda_raw_topics = lda.show_topics(-1)
        #lda_pretty_topics = prettify(lda.show_topics(-1))
        #lda_topic_distribution = [l for l in lda[tfidf_corpus]]

    except:
        status_code = 500
        print(traceback.print_exc())

    return status_code
