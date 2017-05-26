'''
Created on 16-Apr-2017

@author: shaina
'''
import pickle
import Searching

comapany  = ['Google India private Limited', 'Facebook India', 'Microsoft India' 'Amazon India', 'Adobe India', 'D.E. Shaw India'];
aspect = ['market', 'location', 'employee', 'customer', 'technology', 'work culture'];

#reading ontology and domain words
features = pickle.load(open("E:/major2_data/onto.p", "rb"))
domain_words = pickle.load(open("E:/major2_data/domain_words.p", "rb"))


Searching.searchTwitter('Amazon ', 'work culture')
