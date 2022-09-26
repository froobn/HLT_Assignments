import random
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag

text = open('WordGuessGame/anat19.txt')
text = text.read()
# PREPROCESSING
def preprocess():
    wnl = WordNetLemmatizer()

    # process into tokens with unique set
    tokens = [t.lower() for t in word_tokenize(text)]
    tokens = [t for t in tokens if t.isalpha() and
        t not in stopwords.words('english') and len(t) > 5]
    tokenset = set(tokens)

    # process lemmas with unique set
    lemmas = [wnl.lemmatize(t) for t in tokens]
    lemmas_unique = list(set(lemmas))
    tagged_lemmas = pos_tag(lemmas_unique)

    # get nouns
    nouns = []
    for word, tag in tagged_lemmas:
        if tag == 'NN':
            nouns.append(word)
    
    # print ifo
    for x in range(20):
        print(tagged_lemmas[x])
    print(len(nouns))
    print("\nLexical diversity: %.2f" % (len(tokenset) / len(tokens)))

    return tokens, nouns

# GUESSING GAME
def guessing_game():
    points = 5
    letters_guessed = []
    letter = ""
    word = random.choice(wordlist)

    while letter != "!" and points >= 0: # main control loop + LOSE CONDITION

        # get string to print        
        print_string = ""
        for i, c in enumerate(word):
            if c in letters_guessed:
                print_string += c + " "
            else:
                print_string += "_ "

        print(print_string)
        if "_" not in print_string: # WIN CONDITION
            print("You Win!")
            return

        letter = input("Guess a letter: ")
        while len(letter) != 1 or letter in letters_guessed:
            letter = input()

        letters_guessed.append(letter)
        if letter in word: 
            points += 1
            print("Right! Score is " + str(points))
        else:
            points -= 1
            if points < 0:
                break
            print("Sorry, guess again. Score is " + str(points))
    
    print("You Lose!")


tokens, nouns = preprocess()

# set noun dictionary
noun_dict = {}
for noun in nouns:
    noun_dict[noun] = tokens.count(noun)

# sort dictionary
sorted = sorted(noun_dict.items(), key=lambda x:x[1], reverse = True)
sorted_dict = dict(sorted)

# get wordlist
wordlist = list(sorted_dict.items())[:50]
print(wordlist)
wordlist = list(zip(*wordlist))[0] # set wordlist equal to only the words, not their count

guessing_game()

