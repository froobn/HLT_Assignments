import sys
import nltk
from nltk.util import ngrams
import pickle
  
def format_text(filename):
    file = open(filename, encoding='utf-8')
    file_text = file.read()
    file_text = file_text.replace('\n', '')
    tokens = nltk.word_tokenize(file_text)
    bigrams = ngrams(tokens,2)
    unigrams = ngrams(tokens,1)
    bgram_dict = nltk.FreqDist(bigrams)
    ugram_dict = nltk.FreqDist(unigrams)
    return bgram_dict, ugram_dict

def main():
    languages = ['English', 'French', 'Italian']

    for language in languages:
        print("formatting: " + language)
        bigram, unigram = format_text('NGrams/LangId.train.'+language)
        output_file = open('NGrams/'+language, 'ab')
        pickle.dump([bigram,unigram], output_file)
        output_file.close()

main()