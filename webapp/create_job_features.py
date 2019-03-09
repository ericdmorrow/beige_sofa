# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 21:30:35 2018

@author: Eric
"""

#todo;
# precompute job feature matrix and vectorizer save as picked files


#%%
import numpy
import math
from operator import itemgetter
import numpy
import os

import pickle

from LemmaTokenizer import LemmaTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer

#https://marcobonzanini.com/2015/03/02/mining-twitter-data-with-python-part-1/

#%%
#from nltk import word_tokenize, wordpunct_tokenize          
#from nltk.stem import WordNetLemmatizer 
#class LemmaTokenizer(object):
#    def __init__(self):
#        self.wnl = WordNetLemmatizer()
#    def __call__(self, doc):
#        return [self.wnl.lemmatize(t) for t in wordpunct_tokenize(doc)]

#%%
class rec_server:
    def __init__(self):
        # New article feeds
        self.job_dir = 'job_descriptions'
        
    def create_career_featurematrix(self, fname):
        print('Creating career feature matrix')
        self.cvectorizer = TfidfVectorizer(tokenizer=LemmaTokenizer(), sublinear_tf=True, max_df=0.95, min_df=2, max_features=1000,stop_words='english')
        self.X_careers = self.cvectorizer.fit_transform([self.job_descriptions[key] for key in self.job_descriptions.keys()])
        tmpM = self.X_careers.todense()
        tmpM.dump(fname)


    def define_career_desc(self):
        print('Loading job descriptions')
        #list the files in the folder
        jfiles = os.listdir(self.job_dir)
    
        #create a dictionary where key is filename; content is value
        job_descriptions = {}
        for file in jfiles:
            with open(self.job_dir + '/' + file, 'r') as f:
                job_descriptions[file.split('.')[0]] = f.read().replace('\n',' ')
        self.job_descriptions = job_descriptions

    def pickle_vectorizer(self, fname):
        with open(fname, 'wb') as fin:
            pickle.dump(self.cvectorizer, fin)


if __name__ == "__main__":
    #%%
    RS = rec_server()
    RS.define_career_desc()
    RS.create_career_featurematrix('job_feature_matrix.dat')
    RS.pickle_vectorizer('vectorizer.pk')