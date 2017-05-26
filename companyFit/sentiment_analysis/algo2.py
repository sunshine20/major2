'''
Created on 23-May-2017

@author: shaina
'''
import json
import nltk
from nltk.corpus import sentiwordnet as swn
from _overlapped import NULL
import pickle
from itertools import islice
from nltk.parse.stanford import StanfordDependencyParser
import csv
# create parser instance
dep_parser = StanfordDependencyParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")

mpqa = pickle.load(open("E:/major2_data/mpqa.p", "rb"))


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
  
# end


def checkIfTarget(tupple):
    word = tupple[0]
    pos = tupple[1]
    if(pos == 'NN' and word.lower() not in mpqa):
        return True
    else:
        return False
# end


def checkIfOpinion(tupple):
    word = tupple[0]
    pos = tupple[1]
    if((pos == 'NN' or pos == 'JJ' or pos == 'VB') and (word.lower() in mpqa)):    
        return True
    else:
        return False
# end


def checkIfMatch(tupple1, tupple2):
    if (tupple1[0] == tupple2[0] and tupple1[1] == tupple1[1]):    
        return True
    else:
        return False
    
# end    
 
def findFOP(sentence):
    result = dep_parser.raw_parse(sentence)
    dep = result.__next__()
    DT = list(dep.triples()) 
    print(DT)
    
    DT_mapped = []  
    visited = {}
    dependency = {}
    for i in range(len(DT)):
        relation = DT[i][1]
        head = (DT[i][0][0], mapPosTag(DT[i][0][1]))  # mapping POS tags in DT 
        dependent = (DT[i][2][0], mapPosTag(DT[i][2][1]))
        DT_mapped.append((relation, head, dependent))  # creating new list
        visited[(relation, head, dependent)] = False  # setting visited to false for all dependencies initially
        # creating dictionary from dependency list
        if(relation not in dependency):
            dependency[relation] = [(head, dependent)]
        else:
            dependency[relation].append((head, dependent)) 
    
    print(DT_mapped)
    
    for key, value in dependency.items():
        print(key)
        print(value)
        
    FEATURES = []
    FOP = []
        
    
    for i in range(len(DT_mapped)):
        if(visited[DT_mapped[i]] == False):
            relation = DT_mapped[i][0]
            head = DT_mapped[i][1]
            dep = DT_mapped[i][2]
            
            if(relation == 'nsubj'):      
                                         
                if(checkIfOpinion(head) and checkIfTarget(dep)):         #rule 1
                    FEATURES.append(dep[0])                              #storing only word for feature
                    FOP.append([dep[0], list(head)])                           #storing word and pos for opinion
                    visited[DT_mapped[i]]= True
                    
                    rel = 'compound'                                      #rule2
                    if(rel in dependency):
                        for k in range(len(dependency[rel])):
                            t2 = dependency[rel][k][0]
                            t1 = dependency[rel][k][1]
                            if(visited[(rel,t2,t1)] == False):
                                
                                if(checkIfMatch(dep,t2)):
                                    FEATURES.append(t1[0] + ' ' + t2[0])
                                    FOP.append([t1[0] + ' ' + t2[0] , list(head)])
                                    #visited[(rel,t2,t1)] = True    #not set vivited for compound and conj dependency
                     
                
                
                elif(checkIfTarget(head) and checkIfOpinion(dep)):          #rule3
                    FEATURES.append(head[0])
                    FOP.append([head[0], list(dep)])
                    visited[DT_mapped[i]] = True
                    
                    
                    rel = 'compound'                                      
                    if(rel in dependency):
                        for k in range(len(dependency[rel])):
                            o1 = dependency[rel][k][0]
                            o2 = dependency[rel][k][1]
                            if(visited[(rel,o1,o2)] == False):
                                
                                if(checkIfMatch(dep,o2) and checkIfOpinion(o1)):
                                    FEATURES.append(head[0])        #keeping redundant features to find count at end
                                    FOP.append([head[0], list(o1)])
                                    #visited[(rel,o1,o2)] = True
                    
                
                elif(checkIfOpinion(head) and not checkIfTarget(dep) and not checkIfOpinion(dep)):
                    h = dep
                    f = 0
                    
                    rel = 'dobj'                                            #rule5
                    if(rel in dependency):
                        for k in range(len(dependency[rel])):
                            o = dependency[rel][k][0]
                            t = dependency[rel][k][1]
                            if(visited[(rel,o,t)] == False):
                               
                                if(checkIfMatch(head, o) and checkIfTarget(t)):
                                    FEATURES.append(t[0])
                                    FOP.append([t[0], list(o)])
                                    visited[(rel,o,t)] = True
                                    f = 1
                                    
                    
                    rel = 'xcomp'                                            #rule4
                    if(rel in dependency):
                        for k in range(len(dependency[rel])):
                            o = dependency[rel][k][0]
                            w = dependency[rel][k][1]
                            if(visited[(rel,o,w)] == False):
                                flag = 0
                                
                                if(checkIfMatch(head,o) and not checkIfOpinion(w) and not checkIfTarget(w)):
                                    rel2 = 'dobj'
                                    if(rel2 in dependency):
                                        for p in range(len(dependency[rel2])):
                                            w1 = dependency[rel2][p][0]
                                            t2 = dependency[rel2][p][1]
                                            if(visited[(rel2,w1,t2)] == False):
                                                
                                                if(checkIfMatch(w, w1) and checkIfTarget(t2)):
                                                    FEATURES.append(t2[0])
                                                    FOP.append([t2[0], list(o)])
                                                    visited[(rel2,w1,t2)] = True
                                                    flag = 1
                                                    f = 1
                                                    
                                                    rel3 = 'compound'
                                                    if(rel3 in dependency):
                                                        for m in range(len(dependency[rel3])):
                                                            t3 = dependency[rel3][m][0]
                                                            t4 = dependency[rel3][m][1]
                                                            if(visited[(rel3,t3,t4)] == False):
                                                                
                                                                if(checkIfMatch(t2,t3) and checkIfTarget(t4)):
                                                                    FEATURES.append(t4[0] + ' ' + t3[0])
                                                                    FOP.append([t4[0] + ' ' + t3[0], list(o)])
                                    if(flag):
                                        visited[rel,o,w] = True                           
                                                    
                                                        
                    rel = 'nmod'                            #rule6
                    if(rel in dependency):
                        for k in range(len(dependency[rel])):
                            o = dependency[rel][k][0]
                            t = dependency[rel][k][1]
                            if(visited[(rel,o,t)] == False):
                                if(checkIfMatch(head, o) and checkIfTarget(t)):
                                    FEATURES.append(t[0])
                                    FOP.append([t[0], list(o)])
                                    visited[(rel,o,t)] = True
                                    f = 1
                                    
                                    rel2 = 'compound'
                                    if(rel2 in dependency):
                                        for p in range(len(dependency[rel2])):
                                            t2 = dependency[rel2][p][0]
                                            t1 = dependency[rel2][p][1]
                                            if(visited[(rel2,t2,t1)] == False):
                                                if(checkIfMatch(t,t2) and checkIfTarget(t1)):
                                                    FEATURES.append(t1[0] + ' ' + t2[0])
                                                    FOP.append([t1[0] + ' ' + t2[0], list(o)])
                                                
                    
                                                        
                    if(f):                                   
                        visited[DT_mapped[i]] = True                

                
                elif(not checkIfTarget(head)  and not checkIfOpinion(head) and checkIfOpinion(dep)):
                    f = 0
                    
                    rel = 'acomp'           #rule7
                    if(rel in dependency):
                        for k in range(len(dependency[rel])):
                            w = dependency[rel][k][0]
                            t = dependency[rel][k][1]
                            if(visited[(rel,w,t)] == False):
                                if(checkIfMatch(head, w) and checkIfTarget(t)):
                                    FEATURES.append(t[0])
                                    FOP.append([t[0], list(dep)])
                                    visited[(rel,w,t)] = True
                                    f = 1
                                    
                    
                    rel = 'nmod'            #rule8
                    if(rel in dependency):
                        for k in range(len(dependency[rel])):
                            w = dependency[rel][k][0]
                            t = dependency[rel][k][1]
                            if(visited[(rel,w,t)] == False):
                                if(checkIfMatch(head, w) and checkIfTarget(t)):
                                    FEATURES.append(t[0])
                                    FOP.append([t[0], list(dep)])
                                    visited[(rel,w,t)] = True
                                    f = 1
                                    
                    
                    if(f):
                        visited[DT_mapped[i]] = True
                
                
                #rule10
                elif( not checkIfTarget(head) and not checkIfOpinion(head) and not checkIfTarget(dep) and not checkIfOpinion(dep)):
                    #rel = 'acomp'
                    rel = 'xcomp'
                    if(rel in dependency):
                        for k in range(len(dependency[rel])):
                            w = dependency[rel][k][0]
                            o = dependency[rel][k][1]
                            if(visited[(rel,w,o)] == False):
                                flag = 0
                                if(checkIfMatch(head, w)  and checkIfOpinion(o)):
                                    #rel2 = 'rcmod'
                                    rel2 = 'acl:relcl'
                                    if(rel2 in dependency):
                                        for p in range(len(dependency[rel2])):
                                            t = dependency[rel2][p][0]
                                            w1 = dependency[rel2][p][1]
                                            if(visited[(rel2,t,w1)] == False):
                                                if(checkIfTarget(t) and checkIfMatch(w,w1)):
                                                    FEATURES.append(t[0])
                                                    FOP.append([t[0], list(o)])
                                                    visited[(rel2,t,w1)] = True
                                                    flag = 1
                                                    
                                                    
                                                    rel3 = 'compound'
                                                    if(rel3 in dependency):
                                                        for m in range(len(dependency[rel3])):
                                                            t3 = dependency[rel3][m][0]
                                                            t4 = dependency[rel3][m][1]
                                                            if(visited[(rel3,t3,t4)] == False):
                                                                
                                                                if(checkIfMatch(t,t3) and checkIfTarget(t4)):
                                                                    FEATURES.append(t4[0] + ' ' + t3[0])
                                                                    FOP.append([t4[0] + ' ' + t3[0], list(o)])
                                    if(flag):
                                        visited[(rel,w,o)] = True
                                        visited[DT_mapped[i]] = True
                                        
                                               
                elif(not checkIfOpinion(head) and not checkIfTarget(head)  and checkIfTarget(dep)):
                    rel = 'xcomp'
                    if(rel in dependency):
                        for k in range(len(dependency[rel])):
                            w = dependency[rel][k][0]
                            o = dependency[rel][k][1]
                            if(visited[(rel,w,o)] == False):
                                if(checkIfMatch(head, w) and checkIfOpinion(o)):
                                    FEATURES.append(dep[0])
                                    FOP.append([dep[0], list(o)])
                                    visited[(rel,w,o)] = True
                                    visited[DT_mapped[i]] = True    
                    
                
            elif(relation == 'amod'):                                        #rule11
                if(checkIfTarget(head) and checkIfOpinion(dep)):
                    FEATURES.append(head[0])
                    FOP.append([head[0], list(dep)])
                    visited[DT_mapped[i]] = True
                    
                    rel = 'amod'                                            #rule12
                    if(rel in dependency):
                        for k in range(len(dependency[rel])):
                            o1 = dependency[rel][k][0]
                            o2 = dependency[rel][k][1]
                            if(visited[(rel,o1,o2)] == False):
                                
                                if(checkIfMatch(dep, o1) and checkIfOpinion(o2)):
                                    FEATURES.append(head[0])
                                    FOP.append([head[0], list(o2)])
                                    visited[(rel,o1,o2)] = True     
                                    
                    rel = 'conj'                        #rule13
                    if(rel in dependency):
                        for k in range(len(dependency[rel])):
                            o1 = dependency[rel][k][0]
                            o2 = dependency[rel][k][1]
                            if(visited[(rel,o1,o2)] == False):
                                
                                if(checkIfMatch(dep, o1) and checkIfOpinion(o2)):
                                    FEATURES.append(head[0])
                                    FOP.append([head[0], list(o2)])
                                    visited[(rel,o1,o2)] = True                      
                    
                    
                    rel = 'conj'                        #rule14,15
                    if(rel in dependency):
                        for k in range(len(dependency[rel])):
                            t1 = dependency[rel][k][0]
                            t2 = dependency[rel][k][1]
                            if(visited[(rel,t1,t2)] == False):
                                
                                if(checkIfMatch(head, t1) and checkIfTarget(t2)):
                                    FEATURES.append(t2[0])
                                    FOP.append([t2[0], list(dep)])
                                    visited[(rel,t1,t2)] = True    
                                    
                                    rel2 = 'compound'
                                    if(rel2 in dependency):
                                        for p in range(len(dependency[rel2])):
                                            t3 = dependency[rel2][p][0]
                                            t4 = dependency[rel2][p][1]
                                            if(visited[(rel2,t3,t4)] == False):
                                                if(checkIfMatch(t2, t3) and checkIfTarget(t4)):
                                                    FEATURES.append(t4[0] + ' ' + t3[0])
                                                    FOP.append([t4[0] + ' ' + t3[0], list(dep)])
                                                              
                    
                
                elif(checkIfTarget(head) and not checkIfOpinion(dep) and not checkIfTarget(dep)):  #rule16
                    f = 0
                    rel = 'amod'
                    if(rel in dependency):
                        for k in range(len(dependency[rel])):
                            w1 = dependency[rel][k][0]
                            o = dependency[rel][k][1]
                            if(visited[(rel,w1,o)] == False):
                               
                                if(checkIfMatch(dep, w1) and checkIfOpinion(o)):
                                    FEATURES.append(head[0])
                                    FOP.append([head[0], list(o)])
                                    visited[(rel,w1,o)] = True  
                                    f = 1
                                    
                    rel = 'conj'
                    if(rel in dependency):
                        for k in range(len(dependency[rel])):
                            w1 = dependency[rel][k][0]
                            o = dependency[rel][k][1]
                            if(visited[(rel,w1,o)] == False):
                               
                                if(checkIfMatch(dep, w1) and checkIfOpinion(o)):
                                    FEATURES.append(head[0])
                                    FOP.append([head[0], list(o)])
                                    visited[(rel,w1,o)] = True  
                                    f = 1
                    if(f):
                        visited[DT_mapped[i]] = True                
                 
                
                elif(not checkIfTarget(head) and not checkIfOpinion(head)  and checkIfOpinion(dep)):
                    rel = 'conj'
                    if(rel in dependency):
                        for k in range(len(dependency[rel])):
                            w1 = dependency[rel][k][0]
                            t = dependency[rel][k][1]
                            if(visited[(rel,w1,t)] == False):
                                if(checkIfMatch(head, w1) and checkIfTarget(t)):
                                    FEATURES.append(t[0])
                                    FOP.append([t[0], list(dep)])
                                    visited[(rel,w1,t)] = True
                                    visited[DT_mapped[i]] = True
                        
                                       
                
            elif(relation == 'nmod'):
                if(checkIfOpinion(head) and checkIfTarget(dep)):              #rule19
                    FEATURES.append(dep[0])
                    FOP.append([dep[0], list(head)])
                    visited[DT_mapped[i]]= True
                    
                    rel = 'compound'                                          #rule20
                    if(rel in dependency):
                        for k in range(len(dependency[rel])):
                            t2 = dependency[rel][k][0]
                            t1 = dependency[rel][k][1]
                            if(visited[(rel,t2,t1)] == False):
                                if(checkIfMatch(dep,t2) and checkIfTarget(t1)):
                                    FEATURES.append(t1[0] + ' ' + t2[0])
                                    FOP.append([t1[0] + ' ' + t2[0], list(head)])                                                         
                
               
                    
                                                                                 
                    
                    
                
            elif(relation == 'dobj'):                                          #rule23
                if(checkIfOpinion(head) and checkIfTarget(dep)):
                    FEATURES.append(dep[0])
                    FOP.append([dep[0], list(head)])
                    visited[DT_mapped[i]]= True
                    
                    
            #elif(relation == 'acomp'):
                
            #elif(relation == 'xcomp'):
                
    
    #adding neg flag to all opinion
    if(FOP):
        for k in range(len(FOP)):
            FOP[k][1].append('0')
        
    #handling negation(not,never)
    rel = 'neg'
    if(rel in dependency):
        for k in range(len(dependency[rel])):
            o = dependency[rel][k][0]
            o_word = o[0]
            o_pos = o[1]
           
            
            for p in range(len(FOP)):
                opinion =  FOP[p][1]
                opinion_word = opinion[0]
                opinion_pos = opinion[1]
                
                if(o_word == opinion_word and o_pos == opinion_pos):
                    FOP[p][1][2] = '1'
                 

    #handling negation(no)
    rel = 'det'
    if(rel in dependency):
        for k in range(len(dependency[rel])):
            if(dependency[rel][k][1][0] == 'no'):
                o = dependency[rel][k][0]
                o_word = o[0]
                o_pos = o[1]
           
            
                for p in range(len(FOP)):
                    opinion =  FOP[p][1]
                    opinion_word = opinion[0]
                    opinion_pos = opinion[1]
                    
                    if(o_word == opinion_word and o_pos == opinion_pos):
                        FOP[p][1][2] = '1'
                 
                
                
             
                                      
    return FEATURES, FOP   
        
# end    

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


def findFOS(FOP):
    FOS = []
    for k in range(len(FOP)):
        feature = FOP[k][0]
        opinion = FOP[k][1]
        opinion_word = opinion[0]
        opinion_pos = opinion[1]
        change_sign = opinion[2]
        score = findSentiScoreWithTag(opinion_word, mapPOSforSWN(opinion_pos))
        if(change_sign == '1'):
            score = -1*score
        normalized_score = findNormalizedScore(score)
        
        FOS.append((feature, (opinion_word, score, normalized_score)))
    
  
    #merge opinions for same feature
    f = {}
    for k in range(len(FOS)):
        feature = FOS[k][0]
        opinion = FOS[k][1]
        if(feature not in f):
            f[feature]=[opinion]
        else:
            f[feature].append(opinion)
    '''       
    for k, v in f.items():
        print(k)
        print(v)        
    '''
    
    FFOS = []
    for key, value in f.items():
        FFOS.append((key,value))
    return FFOS    
        

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

'''
review = "Best selling items :--RRB- Samsung On5 Pro @ INR 7990 / - | Buy Samsung On5 Pro Gold Online at Best Price in India - Amazon.in Samsung Split AC -LRB- 1.5 Ton 5 Star -RRB- @ INR 7710 / - OFF on INR 41700 / - | Sanyo 43 Inches Full HD LED IPS TV Price : Buy Sanyo 43 Inches Full HD LED IPS Black Television Online India Apple iPhone 6 -LRB- 32GB -RRB- @ INR 26499 / - | Buy iphone 6 32 GB Online at Best Price in India - Amazon.in Kindle Paperwhite @ INR 8999 / - + Kindle Unlimited worth INR 999 / - FREE | Kindle Paperwhite BPL 80cm -LRB- 32 -RRB- HD Ready LED TV @ INR 13990 / - | BPL 32 Inches HD Ready LED TV Price : Buy BPL 80cm Vivid HD Ready Black LED TV Online at Best Price in India Titan Women 's Watch @ INR 4195 / - | www.amazon.in/dp/B071CTX49P Philips Trimmers @ Min 20 % OFF / - | Buy Men 's Philips Beard Trimmer Cordless Online at Best Price in India - Amazon.in Hope it helps."   
s = splitIntoSentences(review)
for k in range(len(s)):
    print(k)
    sent = s[k][:100] 
    #sent = " work culture and management culture is awesome."
    f,fop=findFOP(sent)
    fos=findFOS(fop)
    print(f)
    print(fop)
    print(fos)   
''' 
'''
filename = "E:\\major2_data\\amazon_gd.csv"   
dataset,dataTag = readDataset(filename) 


#dict_F = {}
#dict_FOS = {}
for key, value in dataset.items():
    f = []
    fop = []
    fos = []
    sentences = splitIntoSentences(value)
    for m in range(len(sentences)):
        features,  pairs = findFOP(sentences[m])
        scores = findFOS(pairs)
        f += features
        fop += pairs
        fos += scores
    with open("E:\\major2_data\\amazon_gd_algo2_features.csv", 'a') as a:
        f_writer = csv.writer(a)     
        f_writer.writerow([key,json.dumps(f)])
    with open("E:\\major2_data\\amazon_gd_algo2_fos.csv", 'a') as b:
        fos_writer = csv.writer(b)          
        fos_writer.writerow([key,json.dumps(fos)])        
    #dict_F[key] = f
    #dict_FOS[key] = fos    
        
'''        


