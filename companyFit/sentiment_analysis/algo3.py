'''
Created on 24-May-2017

@author: shaina
'''

import nltk
import json
from nltk.corpus import sentiwordnet as swn
from _overlapped import NULL
from itertools import islice
import pickle
import csv
# noun phrase patterns
P = ['NN', 'NN NN', 'JJ NN', 'NN NN NN', 'JJ NN NN', 'JJ JJ NN', 'NN IN NN', 'NN IN DT NN']
mpqa = pickle.load(open("E:/major2_data/mpqa.p", "rb"))

def extractFeatures(sentence):
    PC = []
    tagged_sentence = tagSentence(sentence)
    n = len(tagged_sentence)
    for i in range(1, n + 1):
        if i < (n - 2):
            x = 3
        elif i == (n - 2):
            x = 2
        elif i == (n - 1):
            x = 1
        else:
            x = 0
                        
        for j in range(x, -1, -1):
            GT = []
            GW = []
            for k in range(i, i + j + 1):
                GT.append(mapPosTag(tagged_sentence[k - 1][1]))  # lists are indexed from 0
                GW.append(tagged_sentence[k - 1][0])
            tag = ' '.join(GT)
            word = ' '.join(GW)
            if tag in P :
                i = i + j
                PC.append(word)
                break   
    
    return PC            
#end   

 
    
def tagSentence(sentence):
    t = nltk.tokenize.word_tokenize(sentence)
    tagged_sentence = nltk.pos_tag(t)
    new_tagged_sentence = []
    for i in range(len(tagged_sentence)):
        word = tagged_sentence[i][0]
        postag = tagged_sentence[i][1]
        new_tagged_sentence.append((word, postag, i + 1)) 
        
    return new_tagged_sentence    
#end 

 
# mapping pos tag to one used in algo
def mapPosTag(tag):
    if tag in ('NN', 'NNS', 'NNP', 'NNPS') :
        return 'NN'
    elif tag in ('JJ', 'JJR', 'JJS') :
        return 'JJ'
    elif tag in ('RB', 'RBR', 'RBS'):
        return 'RB'
    elif tag in ('VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'):
        return 'VB'
    else:
        return tag
  
#end


def readDataset(filename):
    f = open(filename, 'rU')
    dataset = {}
    dataTag = {}
    for line in islice(f,1,10):
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
   

def findFOP(raw_features, tag):
    features = []
    fop = []
    
    for k in range(len(raw_features)):
        f = raw_features[k].split(' ')
        
        if(len(f) == 1):
            if(tag == 'c' or tag == 'p'):
                features.append(f[0])
                fop.append((f[0], tag))
                
        elif(len(f) == 2):
            if(f[0].lower() in mpqa):
                features.append(f[1])
                fop.append((f[1], f[0]))
            elif(tag == 'c' or tag == 'p'):
                features.append(' '.join(f))
                fop.append((' '.join(f), tag))
                
        elif(len(f) == 3):
            if(f[0].lower() in mpqa):
                features.append(f[1] + ' ' + f[2])
                fop.append((f[1] + ' ' + f[2], f[0]))    
            elif(tag == 'c'  or tag == 'p'):
                features.append(f[1] + ' ' + f[2])
                fop.append((f[1] + ' ' + f[2], tag))      
                
    features = list(set(features))
    fop = list(set(fop))
                      
    return features, fop   
#end


def findFOS(fop):   
    fos = []
    for k in range(len(fop)):
        f = fop[k][0]
        op = fop[k][1]
        
        if(op == 'p'):
            op = 'pro'
            score = +1
            normalized_score = +1
            
        elif(op == 'c'):
            op = 'con'
            score = -1
            normalized_score = -1
        else:
            score = findSentiScore(op)    
            normalized_score =  findNormalizedScore(score)
           
        fos.append((f, (op, score, normalized_score)))    
        
    #combining opinions for same feature into a list
    f = {}
    for k in range(len(fos)):
        feature = fos[k][0]
        opinion = fos[k][1]
        if(feature not in f):
            f[feature]=[opinion]
        else:
            f[feature].append(opinion)
    
    
    FFOS = []
    for key, value in f.items():
        FFOS.append((key,value))    
               
        
    return FFOS 
    
#end     


def findSentiScore(word):
    synsets = list(swn.senti_synsets(word)) 
    n = len(synsets)
    if(n == 0):
        return None

    pscore = 0.0
    nscore = 0.0
    # taking average of scores coz sorting of synsets according to sense number not possble
    for i in range(0, n):
        pscore += synsets[i].pos_score() 
        nscore += synsets[i].neg_score()
        
    pscore = pscore / n
    nscore = nscore / n     
       
    # return max if different..if same check value from output of machine learning
    if(nscore > pscore):
        return -1 * nscore
    elif(nscore < pscore):
        return pscore
    
    else:  
        return 0.0
#end     

def findNormalizedScore(score):
    if(score is None):
        return None
    elif(score <= -0.5):
        return -2
    elif(score > -0.5 and score < 0 ):
        return -1
    elif(score == 0):
        return 0
    elif(score > 0 and score < 0.5):
        return +1
    elif(score >= 0.5):
        return +2     
#end    

'''
filename = "E:\\major2_data\\amazon_gd.csv"   
dataset,dataTag = readDataset(filename)   

for key, value in dataset.items():
    print(key)
    f = []
    fop = []
    fos = []
    sentences = splitIntoSentences(value)
    for k in range(len(sentences)):
        raw_features = extractFeatures(sentences[k]) 
        if(raw_features ):
            features, pairs = findFOP(raw_features, dataTag[key])
            scores = findFOS(pairs)
            f += features
            fop += pairs
            fos += scores
    with open("E:\\major2_data\\amazon_gd_algo3_features.csv", 'a') as a:
        f_writer = csv.writer(a)     
        f_writer.writerow([key,json.dumps(f)])
    with open("E:\\major2_data\\amazon_gd_algo3_fos.csv", 'a') as b:
        fos_writer = csv.writer(b)          
        fos_writer.writerow([key,json.dumps(fos)])              
     
'''        
     
    



'''
sent = "Awesome work culture and management culture."
f = extractFeatures(sent)
print(f)
'''
            