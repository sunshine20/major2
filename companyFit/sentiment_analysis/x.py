'''
Created on 23-Apr-2017

@author: shaina
'''
'''
import os
java_path = "C:/Java/jdk1.8.0_05/bin/java.exe"
os.environ['JAVAHOME'] = java_path
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize

# Change the path according to your system
stanford_classifier = 'C:\Python\Python35-32\stanford-ner-2015-12-09\classifiers\english.all.3class.distsim.crf.ser.gz'
stanford_ner_path = 'C:\Python\Python35-32\stanford-ner-2015-12-09\stanford-ner.jar'

# Creating Tagger Object
st = StanfordNERTagger(stanford_classifier, stanford_ner_path, encoding='utf-8')

text = 'While in France, Christine Lagarde discussed short-term stimulus efforts in a recent interview with the Wall Street Journal.'

tokenized_text = word_tokenize(text)
classified_text = st.tag(tokenized_text)

print (classified_text)
'''

