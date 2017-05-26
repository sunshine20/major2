'''
Created on 13-Apr-2017

@author: shaina
'''

from nltk.corpus import wordnet as wn
import pickle


# defining basic ontology
comapany = ['google', 'facebook', 'microsoft' 'amazon', 'adobe', 'de shaw'];
aspect = ['market', 'location', 'employee', 'customer', 'technology', 'work culture'];
features = {};
features['market'] = [['profit'], ['status'], ['share'], ['revenue'], ['stock value'],
                      ['size'], ['competition'], ['threat'], ['trend'], ['reputation'],
                      ['position'], ['strength']];
features['location'] = [['infrastructure'], ['weather'], ['food'], ['connectivity'], ['facilities']];
features['employee'] = [['benefit'], ['engagement'], ['friendly'], ['centric'], ['satisfaction'],
                        ['salary'], ['hikes'], ['promotion'], ['recreation'], ['opportunity'],
                        ['growth'], ['learn'], ['personal development'], ['onsite'], ['rewards'],
                        ['competition'], ['threat'], ['skills']];
features['customer'] = [['satisfaction'], ['centric'], ['care']];
features['technology'] = [['trends'], ['methods']];
features['work culture'] = [['timings'], ['hierarchy'], ['atmosphere'], ['recreation'],
                            ['well-being'], ['quality'], ['facilities'], ['competition'], ['restriction'],
                            ['management'], ['training'], ['mobility']]
 
domain_words = ['market', 'location', 'employee', 'customer', 'technology', 'work culture', 'profit',
                'status', 'share', 'competition', 'threat', 'trend', 'reputation', 'position', 'strength',
                'infrastructure', 'weather', 'food', 'connectivity', 'facilities', 'benefit', 'engagement',
                'friendly', 'centric', 'satisfaction', 'salary', 'opportunity', 'growth', 'hikes',
                'promotion', 'recreation', 'opportunity', 'growth', 'learn', 'personal development', 'onsite',
                'rewards', 'competition', 'threat', 'skills', 'care', 'methods', 'timings', ' hierarchy',
                 'facilities', 'atmosphere', 'recreation', 'well-being', 'quality', 'restriction',
                 'management', 'training', 'mobility']

print(len(domain_words))

# adding synonyms
for x in aspect:
    y = features[x]
    for i in range(len(y)): 
        lst = y[i]
        word = lst[0]
        for s in wn.synsets(word):
            k = s.name().split('.')[0]
            lst.append(k)
            domain_words.append(k)
        lst = list(set(lst))   
        y[i] = lst
    features[x] = y
domain_words = list(set(domain_words)) 

 
# storing the ontology and domain words
pickle.dump(features, open("E:/major2_data/onto.p", "wb"))
pickle.dump(domain_words, open("E:/major2_data/domain_words.p", "wb")) 
