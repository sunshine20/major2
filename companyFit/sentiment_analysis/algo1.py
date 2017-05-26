'''
Created on 21-Apr-2017

@author: shaina
'''
import csv
import pickle
import nltk
from nltk.parse.stanford import StanfordDependencyParser
from itertools import islice
import json
from nltk.corpus import sentiwordnet as swn
from _overlapped import NULL

# noun phrase patterns
P = ['NN', 'NN NN', 'JJ NN', 'NN NN NN', 'JJ NN NN', 'JJ JJ NN', 'NN IN NN', 'NN IN DT NN']

# read words from GI dictionary
with open('E:/major2_data/GI.csv', 'r') as f:
    reader = csv.reader(f)
    words = list(reader)
    #print(words)
    GI = []
for word in words:
    GI.append(word[0].lower())         #GI contains all words in lower case   
#print(GI)

# read domain words 
domain_words = pickle.load(open("E:/major2_data/domain_words.p", "rb"))

#create parser instance
dep_parser=StanfordDependencyParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")


# tag sentence with pos and word number
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
        
# extract feature (word,pos tag , word no.) from sentence  
# without using domain words
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
    
 
def splitIntoSentences(review):
    sentences = nltk.tokenize.sent_tokenize(review)
    return sentences
#end     
     

def extractFeatureOpinionPairs(sentence, feature_list):
    if len(feature_list) == 0:
        return []
    PS = feature_list               #list of feature candidates in sentence
    result =  dep_parser.raw_parse(sentence)
    dep = result.__next__()
    DT = list(dep.triples())       #list of dependencies in sentence
    print(DT)
    FO = []
    
    for i in range(len(PS)):
        feature = PS[i]
        feature_split = feature.split()  
        rnode = feature_split[-1]       #getting last word of many word feature
        flag = 0
        for j in range(len(FO)):        #Add optimization for repetitive last words
            if rnode in FO[j][0]:       #feature is substring of other feature
                FO.append((feature, FO[j][1]))
                flag = 1
                break
         
        if flag == 0:    
            visited = {}
            for k in range(len(DT)):
                visited[DT[k]] = False
            opinion_list = []    
            getOpinionWord(rnode, DT, visited, opinion_list)
            if len(opinion_list) == 0:
                continue
            else:
                FO.append((feature, opinion_list))
        
    return FO                
#end        


def getOpinionWord(rnode, DT, visited,opinion_list):
    d = []                          #dependencies containing rnode
    for j in range(len(DT)):
        if visited[DT[j]] == False and (DT[j][0][0] == rnode or DT[j][2][0] == rnode):
            d.append(DT[j])
            visited[DT[j]] = True
                
    if len(d) == 0:                 #rnode appears in no dependency
        return                    
    else:
        for k in range(len(d)):
            if d[k][0][0] == rnode :       #getting neighbor and pos of neighbor
                neighbor = d[k][2][0]
                neighbor_pos = d[k][2][1]
            else:
                neighbor = d[k][0][0]
                neighbor_pos = d[k][0][1]    
             
            mapped_neighbor_pos = mapPosTag(neighbor_pos)                    
            if (mapped_neighbor_pos ==  'JJ' )or (mapped_neighbor_pos == 'RB' and neighbor.lower() in GI ):
                opinion_list.append(neighbor)
            else:
                getOpinionWord(neighbor, DT, visited, opinion_list)

#end

                   
def readDataset(filename):
    f = open(filename, 'rU')
    dataset = {}
    dataTag = {}
    for line in islice(f,1,3):
        cells = line.split(',')
        review = cells[4:]
        dataset[cells[1]] = ''.join(review).replace('"""', '')
        dataTag[cells[1]] = cells[3]
    
    f.close()
    return dataset, dataTag  
#end

def findFOP(dataset, dataTag):      #feature,opinion,pair
    dicFOP = {}
    for key, value in dataset.items():
        fop = []
        #print(FOP)
        sentences = splitIntoSentences(value)
        for i in range(len(sentences)):
            sentence = sentences[i]
            features = extractFeatures(sentence)
            featureOpinionPairs = extractFeatureOpinionPairs(sentence, features)
            if(len(featureOpinionPairs) != 0):
                fop += featureOpinionPairs
        dicFOP[key] = fop
        print (fop)
    return dicFOP        
#end    
    
    
def findFOS(dataset, dataTag, dicFOP):
    dicFOS = {}         #feature opinion score
    for key, value in dicFOP.items():
        x = key
        y = []
        for i in range(len(value)):
            feature = value[i][0]
            opinions = list(set(value[i][1]))       #duplicates removed in opinions for a feature
            opi = []
            for j in range(len(opinions)):
                score = findSentiScore(opinions[j])  #pass pos tag of opinion word
                normalized_score = findNormalizedScore(score)
                opi.append( (opinions[j],score,normalized_score))
            y.append ((feature, opi))
        dicFOS[x] = y   
    return dicFOS        
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
        
    
    
def mapPOSforSWN(pos):
    if(pos == 'NN' or pos == 'NNS' or pos == 'NNP' or pos == 'NNPS'):
        return 'n'
    elif(pos == 'VB' or pos == 'VBD' or pos == 'VBG' or pos == 'VBN' or pos == 'VBP' or pos == ' VBZ'):
        return 'v'
    elif(pos == 'JJ' or pos == 'JJR' or pos == 'JJS'):
        return 'a'
    elif(pos == 'RB' or pos == 'RBR' or pos == 'RPS'):
        return 'r'
    else:
        return NULL
#end    
                    
 
def findSentiScoreWithTag(word, pos):
    mapped_pos = mapPOSforSWN(pos)
    if (mapped_pos == NULL):
        return findSentiScore(word)
    else:
        synsets = list(swn.senti_synsets(word, mapped_pos))   
        n = len(synsets)
        if(n == 0):
            return None

        pscore = 0.0
        nscore = 0.0
        
        for i in range(0, n):
            pscore += synsets[i].pos_score() / (i + 1) 
            nscore += synsets[i].neg_score() / (i + 1)
        
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

'''
filename = "E:\\major2_data\\reviews_amazon_india_new5.csv"   
dataset,dataTag = readDataset(filename)   

FOP = findFOP(dataset, dataTag)
FOS = findFOS(dataset, dataTag, FOP)

with open("E:\\major2_data\\amazon_algo1_fos", 'w')as fp:
    json.dump(FOS, fp, sort_keys=True, indent=4)
'''
   
      
sent = "Awesome work culture and management culture."
f = extractFeatures(sent)
print(f)
      



