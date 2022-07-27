#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Per Fallgren

import codecs
import gensim, logging
import os
import sys

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
class MySentences(object):
    def __init__(self, dirname):
        self.dirname = dirname

    def __iter__(self):
        for fname in os.listdir(self.dirname):
            for line in codecs.open(self.dirname + '/' + fname, "r", encoding='utf-8', errors='ignore'):
                yield line.split()

def cbow(dim, win, it):
    fname = 'cbow-' + str(dim) + '-iter' + str(it)+ '-win' + str(win) + '.txt'
    sentences = MySentences("sentences")
    current_model = gensim.models.Word2Vec(sentences,  sg=0, size=dim, window=win, min_count=25, workers=8, hs=0, iter=it)
    f = open(fname, "w")
    current_model.wv.save_word2vec_format(fname, fvocab=None, binary=False)
    f.close()

def sgns(dim, win, it):
    fname = 'sgns-' + str(dim) + '-iter' + str(it)+ '-win' + str(win) + '.txt'
    sentences = MySentences("sentences")
    current_model = gensim.models.Word2Vec(sentences, sg=1, size=dim, window=win, min_count=25, workers=8, hs=0, iter=it)
    f = open(fname, "w")
    current_model.save_word2vec_format(fname, fvocab=None, binary=False)
    f.close()


if __name__ == "__main__":
    if sys.argv[1] == "cbow":
        cbow(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
    elif sys.argv[1] == "sgns":
        sgns(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
    else:
    	print("First parameter should be 'cbow' or 'sgns'")


#  File "create_vectors.py", line 25, in cbow
#    current_model.save_word2vec_format(fname, fvocab=None, binary=False)
#  File "C:\Users\Rebecca\Documents\text-mining-project\env\lib\site-packages\gensim\models\word2vec.py", line 1307, in save_word2vec_format
#    raise DeprecationWarning("Deprecated. Use model.wv.save_word2vec_format instead.")
#DeprecationWarning: Deprecated. Use model.wv.save_word2vec_format instead.
