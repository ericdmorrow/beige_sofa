# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 21:30:35 2018

@author: Eric
"""
#todo;
# remove article recommendation
# precompute job feature matrix and vectorizer; load as picked files


#%%
import feedparser
import numpy
import math
from operator import itemgetter
import numpy as np
import os
import pickle

#https://marcobonzanini.com/2015/03/02/mining-twitter-data-with-python-part-1/

import tweepy
from tweepy import OAuthHandler

from LemmaTokenizer import LemmaTokenizer

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
        
        #Load vectorizer
        with open('vectorizer.pk', 'rb') as fin:
            self.cvectorizer = pickle.load(fin)

        #Load job feature matrix
        self.X_careers = numpy.load("job_feature_matrix.dat")
       
        #Load job descriptions for output
        self.job_dir = 'job_descriptions'
        self.define_career_desc()

        # Twitter extracts
        self.load_twitter_credentials('credentials.txt')
        
        auth = OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_secret)
        self.api = tweepy.API(auth)
    
    def load_twitter_credentials(self, credential_file):
        with open(credential_file, 'r') as f:
            data = f.readlines()
        for line in data:
            varname, value = line.split('=')
            varname = varname.strip()
            value = value.split("'")[1]
            setattr(self, varname, value)
   
    def user_input(self, userinputstr):
        X_user = self.cvectorizer.transform(userinputstr)
        return X_user
    
    def recommend_careers(self, X_user, n):
        similarities = self.X_careers.dot(np.transpose(X_user.todense())) #compute cosine similarity
        recommendations = sorted(zip(self.job_descriptions.keys(), similarities), key=lambda x: x[1], reverse=True)
        return recommendations[:n]
    
    def user_twitter(self, userhandle):
        statuses = self.api.user_timeline(id=userhandle, count=200)
        corpus = ''
        urls = []
        for status in statuses:
            corpus += ' ' + status.text
            if status.entities and status.entities['urls']:
                for url in status.entities['urls']:
                    urls.append(url['expanded_url'])
        return corpus, urls


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

    @staticmethod
    def parse_tweet_urls(urllist):
        kwlist = []
        for url in urllist:
            a = Article(url)
            try:
                a.download()
                a.parse()
                a.nlp()
                kwlist.append(a.keywords)
                del(a)
            except:
                bob = 0
        return kwlist
            


if __name__ == "__main__":
    #%%
    RS = rec_server()
    
    #%% Recommend career based on keywords, job descriptions or twitter statuses
    user_sample = RS.user_input(['financial services'],rtype='career')
    RS.recommend_careers(user_sample, 2)

    user_statuses, user_urls = RS.user_twitter('jk_rowling')
    user_read_articles = RS.parse_tweet_urls(user_urls)
    user_sample = RS.user_input(user_read_articles, rtype='career')
    RS.recommend_careers(user_sample, 3)
    
    #%%
    user_statuses, user_urls = RS.user_twitter('jk_rowling')
    user_sample = RS.user_input([user_statuses])
    RS.recommend_careers(user_sample, 3)
