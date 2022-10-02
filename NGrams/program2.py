import pickle
from nltk.util import ngrams
import nltk

def main():
    languages = ['English', 'French', 'Italian']
    v = 0
    bigrams = []
    unigrams = []
    for language in languages:
        input_pickle = open('NGrams/'+ language, 'rb')     
        input = pickle.load(input_pickle)
        input_pickle.close()
        lang_bigrams = input[0]
        lang_unigrams = input[1]
        v += len(lang_unigrams)
        bigrams.append(lang_bigrams)
        unigrams.append(lang_unigrams)

    with open('NGrams/LangId.results', "w") as results:
        with open('NGrams/LangId.test') as test:
            for line in test:
                tokens = nltk.word_tokenize(line)
                test_bigrams = ngrams(tokens,2)
                prob = [1,1,1]
                for bigram in test_bigrams:
                    for i in range(3):
                        b = bigrams[i][bigram]
                        u = unigrams[i][(bigram[0],)]
                        prob[i] *= ((b + 1) / (u + v))
                max_prob = max(prob)
                lang_index = prob.index(max_prob)
                results.write(['English', 'French', 'Italian'][lang_index] + "\n")
    compare_results()

def compare_results():
    with open('NGrams/LangId.results') as results:
        with open('NGrams/LangId.sol') as solution:
            solution_lines = solution.readlines()
            results_lines = results.readlines()
            count = 0
            incorrect_lines = []
            for i in range(len(solution_lines)):
                sol = solution_lines[i].split()[-1]
                res = results_lines[i]
                if sol.strip() == res.strip():
                    count += 1
                else:
                    incorrect_lines.append(i + 1)

            print(count / len(solution_lines), incorrect_lines)
main()
