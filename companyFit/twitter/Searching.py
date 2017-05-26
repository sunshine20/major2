'''
Created on 06-Apr-2017

@author: shaina
'''
import tweepy
import csv 

def searchTwitter(company,query):
    CONSUMER_KEY = 'J52X3scXSqluPpj2r9iS0whLt'
    CONSUMER_SECRET = 'yIX8J5QzPFXomTxsnZqTUGznesGk0Lc397eOyQJ933VuNayy7S'
    ACCESS_TOKEN = '776309846723272704-tVBOPa9U5loWCnGyi5IxogMLadADpSM'
    ACCESS_SECRET =  'fG37T71Acfd3o3Rnnvr6kDYvHBjWOsYdfaFWvntig2qbi'
        
        
    auth = tweepy.auth.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    
    api = tweepy.API(auth)
    
    # Open/create a file to append data to
    filename = 'E:/major2_data/'+company+'.csv'
    csvFile = open(filename, 'a', encoding = 'utf-8')
    
    #Use csv writer
    csvWriter = csv.writer(csvFile)
    
    for tweet in tweepy.Cursor(api.search, query, lang = "en").items():
        if not 'RT @' in  tweet.text:
            # Write a row to the CSV file. I use encode UTF-8
            csvWriter.writerow([tweet.created_at, tweet.text])
            #print (tweet.created_at)
            #print(tweet.text.encode('utf-8'))
    csvFile.close()
    
