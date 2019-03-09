# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 21:30:35 2018

@author: Eric
"""

#%%
import feedparser
from bs4 import BeautifulSoup as bs
import matplotlib.pyplot as plt
import numpy
import math
from operator import itemgetter
import numpy
import os

from newspaper import Article

from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import TfidfVectorizer

#https://marcobonzanini.com/2015/03/02/mining-twitter-data-with-python-part-1/

import tweepy
from tweepy import OAuthHandler
 
#%%
from nltk import word_tokenize, wordpunct_tokenize          
from nltk.stem import WordNetLemmatizer 
class LemmaTokenizer(object):
    def __init__(self):
        self.wnl = WordNetLemmatizer()
    def __call__(self, doc):
        return [self.wnl.lemmatize(t) for t in wordpunct_tokenize(doc)]

#%%
class rec_server:
    def __init__(self):
        # New article feeds
        self.feeds = [
            'http://www.sfgate.com/rss/feed/Tech-News-449.php',
            'http://feeds.feedburner.com/TechCrunch/startups',
            'http://news.cnet.com/8300-1001_3-92.xml',
            'http://www.zdnet.com/news/rss.xml',
            'http://www.computerweekly.com/rss/Latest-IT-news.xml',
            'http://feeds.reuters.com/reuters/technologyNews',
            'http://www.tweaktown.com/news-feed/'
            'http://feeds.reuters.com/Reuters/worldNews',
            'https://news.google.com/news/rss/headlines/section/topic/WORLD?ned=us&hl=en&gl=US',
            'http://feeds.bbci.co.uk/news/world/rss.xml',
            'https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/section/world/rss.xml'
            'https://www.yahoo.com/news/world/rss',
            'http://rss.cnn.com/rss/edition_world.rss',
            'https://www.theguardian.com/world/rss']
        
        self.article_feed_dir = 'news_feeds'
        self.load_news_feeds()
        self.process_feeds()
        self.create_article_featurematrix()
        
        self.job_dir = 'job_descriptions'
        self.define_career_desc()
        self.create_career_featurematrix()
        
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

    def load_news_feeds(self):
        print('Loading RSS feed sites')
        #list the files in the folder
        files = os.listdir(self.article_feed_dir)

        #create a dictionary where key is filename; content is value
        rss_list = []
        for file in files:
            with open(self.article_feed_dir + '/' + file, 'r') as f:
                rss_list.append(f.readlines())
        self.feeds = [item.strip('\n').strip('\r') for sublist in rss_list for item in sublist]
    
    def process_feeds(self):        
        # for each feed, grab available list of articles and if it contains a summary extract the title and summary words
        self.corpus = []
        self.titles=[]
        
        print('Loading newest feeds')
        for feed in self.feeds:
            d = feedparser.parse(feed)
            for e in d['entries']:
                if 'summary' in e.keys():
                   self.corpus.append(e['summary'])
                   self.titles.append(e['title'])

    def create_article_featurematrix(self):
        print('Creating article feature matrix')
        self.vectorizer = TfidfVectorizer(tokenizer=LemmaTokenizer(), sublinear_tf=True, max_df=0.95, min_df=2, max_features=1000,stop_words='english')
        self.X_articles = self.vectorizer.fit_transform(self.corpus)                
        
    def create_career_featurematrix(self):
        print('Creating career feature matrix')
        self.cvectorizer = TfidfVectorizer(tokenizer=LemmaTokenizer(), sublinear_tf=True, max_df=0.95, min_df=2, max_features=1000,stop_words='english')
        self.X_careers = self.cvectorizer.fit_transform([self.job_descriptions[key] for key in self.job_descriptions.keys()])                

    def user_input(self, userinputstr, rtype='article'):
        if rtype=='article':
            X_user = self.vectorizer.transform(userinputstr)
        else:
            X_user = self.cvectorizer.transform(userinputstr)
        return X_user
    
    def recommend_articles(self, X_user, n):
        similarities = linear_kernel(self.X_articles, X_user) #compute cosine similarity
        recommendations = sorted(zip(self.titles, self.corpus, similarities), key=lambda x: x[2], reverse=True)
        return recommendations[:n]
    
    def recommend_careers(self, X_user, n):
        similarities = linear_kernel(self.X_careers, X_user) #compute cosine similarity
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

    def old_define_career_desc(self):
    #https://targetjobs.co.uk/careers-advice/job-descriptions/276947-advertising-account-executive-job-description
    #https://targetjobs.co.uk/careers-advice/job-descriptions/279903-investment-banker-corporate-finance-job-description
    #https://targetjobs.co.uk/careers-advice/job-descriptions/668041-consultant-job-description
        self.job_descriptions = {'ad_executive': 'Advertising account handlers are employed by advertising agencies to \
                        administer the accounts of a small number of clients (between one and five companies), for \
                        whom they are the key contact. \
                        They are required to know the client and understand exactly what it is that they do and \
                        what it is that they want to sell. \
                        consulting clients about campaign requirements \
                        presenting campaign pitches and costs to clients \
                        passing proposals to appropriate media creative staff \
                        negotiating time-scales and budgets \
                        monitoring work progress and keeping in contact with clients at all stages \
                        delivering final products for review \
                        report writing staff supervision financial administration \
                        The work can be pressurised with tight deadlines. senior managerial positions such as account manager or managing executive.',
                        
                        'investment_banker' : 'Investment bank corporate financiers provide financial services and advice to commercial and government \
                        clients about various financial matters including fund and debt management, mergers, flotations, \
                        acquisitions and privatisation. Corporate financiers are responsible for identifying and securing \
                        privatisation, merger and acquisition deals, managing and investing large monetary funds, and buying and \
                        selling financial products for their clients. working closely with clients at senior levels\
                        advising about how to meet targets and create investment capital \
                        generating finance from shares and loans gathering, analysing and interpreting complicated numerical information \
                        assessing and predicting financial risks and returns using financial modelling to predict outcomes \
                        negotiating and structuring financial details running transactions providing investment advice, tactics and recommendations \
                        preparing legal documents and prospectuses liaising with accountants, lawyers, financial experts and regulatory bodies. \
                        Investment banking provides high levels of responsibility, good promotional opportunities and impressive financial rewards \
                        for the most successful employees. However, working hours are usually very long. Global investment, corporate, retail and commercial banks \
                        Corporate finance sections of accountancy firms Private equity fund institutions The Financial Times and in publications such as Business Week, Investors Chronicle, The Economist and The Banker. Sector and company research is essential. \
                        business studies, management, finance, mathematics or economics qualification can be helpful. MBA \
                        Motivation Ambition Determination Adaptability IT Analytical Teamworking Numerical Problem-solving Communication',
                        
                        'management_consultant' : 'Consultants aim to improve an organisation position or profile by helping to solve problems, manage change and improve efficiency\
                        Consultants offer advice and expertise to organisations to help them improve their business performance in terms of operations, profitability, management, structure and strategy. Although the workload can be heavy, consulting is a \
                        sociable profession with plenty of networking opportunities. The work stretches across a variety of areas, including management, strategy, IT, finance, marketing, HR and supply chain management.\
                        conducting research, surveys and interviews to gain understanding of the business analysing statistics detecting issues and investigating ways to resolve them \
                        assessing the pros and cons of possible strategies compiling and presenting information orally, visually and in writing making recommendations for improvement, using computer models to test them and presenting findings to client \
                        implementing agreed solutions developing and implementing new procedures or training. Most management consultants are employed by international consultancy firms, professional services firms or strategy sections of financial organisations \
                        such as accountants. Consultant firms can range from generalist consultants offering a wide range of services, to specialist consultants within the different business areas, such as strategy or IT. Consultants are \
                        contracted by organisations in all sectors seeking help and advice about business problems. \
                         business, management, economics, mathematics or statistics Commercial awareness Good numerical Attention to detail Analytical  \
                         Excellent interpersonal Tact and persuasive Teamworking IT Good oral and written communication Self-motivation',
                        
                        }
        self.job_infosource = {'ad_executive' : 'https://targetjobs.co.uk/careers-advice/job-descriptions/276947-advertising-account-executive-job-description',
                               'investment_banker' : 'https://targetjobs.co.uk/careers-advice/job-descriptions/279903-investment-banker-corporate-finance-job-description',
                               'management_consultant' : 'https://targetjobs.co.uk/careers-advice/job-descriptions/668041-consultant-job-description'}

    def recommend_career(self, X_user, n):
        similarities = linear_kernel(self.X_articles, X_user) #compute cosine similarity
        recommendations = sorted(zip(self.titles, self.corpus, similarities), key=lambda x: x[2], reverse=True)
        return recommendations[:n]

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
    #%% Recommend new articles based on keywords, job descriptions or twitter statuses
    #%%
    user_sample = RS.user_input(['Elizabeth holmes theranos fraud'])
    print(RS.recommend_articles(user_sample, 3))
    
    #%%
    user_sample = RS.user_input([RS.corpus[0]])
    RS.recommend_articles(user_sample, 3)
    
    #%%
    user_sample = RS.user_input(['kilauea volcano'])
    RS.recommend_articles(user_sample, 3)
    
    #%%
    user_statuses, user_urls = RS.user_twitter('jk_rowling')
    user_sample = RS.user_input([user_statuses])
    RS.recommend_articles(user_sample, 3)
    
    #%% 
    job_desc = RS.job_descriptions['adverstising_account_executive']
    user_sample = RS.user_input([job_desc])
    RS.recommend_articles(user_sample, 3)
    
    #%% 
    job_desc = RS.job_descriptions['investment_fund_manager']
    user_sample = RS.user_input([job_desc])
    RS.recommend_articles(user_sample, 3)
    
    #%% Recommend career based on keywords, job descriptions or twitter statuses
    user_sample = RS.user_input(['financial services'],rtype='career')
    RS.recommend_careers(user_sample, 2)
    
    #%%
    user_statuses, user_urls = RS.user_twitter('jk_rowling')
    user_read_articles = RS.parse_tweet_urls(user_urls)
    user_sample = RS.user_input(user_read_articles, rtype='career')
    RS.recommend_careers(user_sample, 3)
