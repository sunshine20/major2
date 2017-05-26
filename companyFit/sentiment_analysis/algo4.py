'''
Created on 25-May-2017

@author: shaina
'''

import json
import algo3
import algo2
from itertools import islice
import nltk
import csv

def readDataset(filename):
    f = open(filename, 'rU')
    dataset = {}
    dataTag = {}
    for line in islice(f,1,None):
        cells = line.split(',')
        review = cells[4:]
        dataset[cells[1]] = ''.join(review).replace('"""', '')
        dataTag[cells[1]] = cells[3]
    
    f.close()
    return dataset, dataTag  
#end


def splitIntoSentences(review):
    sentences = nltk.tokenize.sent_tokenize(review)
    return sentences
#end 
   
   
filename = "E:\\major2_data\\amazon_gd.csv"   
dataset,dataTag = readDataset(filename)   

count = 0
for key, value in dataset.items():
    #print(key)
    count += 1
    print(count)
    f = []
    fop = []
    fos = []
    sentences = splitIntoSentences(value)
    for k in range(len(sentences)):
        #using algo3
        raw_features = algo3.extractFeatures(sentences[k]) 
        if(raw_features ):
            features, pairs = algo3.findFOP(raw_features, dataTag[key])
            scores = algo3.findFOS(pairs)
            f += features
            fop += pairs
            fos += scores
            
        #using algo2
        features,  pairs = algo2.findFOP(sentences[k][:100])    #limiting sentence length to 100 else parser not works
        scores = algo2.findFOS(pairs)
        f += features
        fop += pairs
        fos += scores    
         
         
    #removing duplicates
    f = list(set(f))
    #fos = list(set(fos))
    
    #placing all opinions of same feature in  a list
    h= {}
    for k in range(len(fos)):
        feature = fos[k][0]
        opinion = fos[k][1]
        if(feature not in h):
            h[feature]= opinion
        else:
            h[feature] += opinion
    
    
    FFOS = []
    for k, v in h.items():
        FFOS.append((k,list(set(v))))    
               
    with open("E:\\major2_data\\amazon_gd_algo4_features.csv", 'a', newline = '') as a:
        f_writer = csv.writer(a)     
        f_writer.writerow([key,json.dumps(f)])
    with open("E:\\major2_data\\amazon_gd_algo4_fos.csv", 'a', newline = '') as b:
        fos_writer = csv.writer(b)          
        fos_writer.writerow([key,json.dumps(FFOS)])          
     
        
     
    


 