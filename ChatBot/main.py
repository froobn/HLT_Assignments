import random
import spacy
from pyswip import Prolog
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.stem import WordNetLemmatizer
import contractions
import string

lemmatizer = WordNetLemmatizer()
sid = SentimentIntensityAnalyzer()
nlp = spacy.load("en_core_web_md")
pl = Prolog()
facts = []
name = None
phrases = {
    "none": [],
    "hello": [['hello','greetings','hi', 'salutations'], 0],
    "goodbye": [['goodbye','bye','talk to you later'],0],
    "name": [['my name is _', 'I am named _', 'You can call me _'], 0],
    "neutral": [["_ is alright, _ is not bad", "I do not hate _", "_ is not the worst", "_ is okay"], 0],
    "like": [["i like _", "_ is tasty", "_ is good", "i am a fan of _", "i love _"], 1],
    "dislike": [["i don't like _", "i dislike _", "i hate _", "_ is horrible", "_ is nasty", "_ is the worst", "_ is not good", "_ is not tasty", "i am not a fan of _"], -1],
    "ask_ingredient": [["what kind of pie uses _", "which pies have _ in them","What pies use _"],0],
    "get_ingredients": [["what ingredients are in _", "what is used in _", "what do i need to make _"], 0],
    "recommend": [["what is your recommendation","what do you recommend?","recommend me a pie", "what is a pie i might like", "find me a pie i would like"],0],
    "bake_time": [["how long does _ take to bake", "how long do i bake _", "what temperature do i bake _ at"],0]
}

responses = {
    "none": ["I don't quite understand.", "I"],
    "hello": ["Hello!", "Hi there!","Salutations fellow pie enjoyer!"],
    "goodbye": ["Goodbye!", "It was nice talking with you!"],
    "name": ["Hello {}!", "Nice to meet you, {}!"],
    "neutral": ["That's understandable."],
    "like": ["Isn't {} great!"],
    "dislike": ["I know a lot of people that feel the same way."],
    "ask_ingredient": ["{} is in the recipe for {}."],
    "get_ingredients": ["{} contains the following:\n {}"],
    "recommend": ["I think you would like {}!"],
    "bake_time": ["{} takes {} minutes at {} degrees."],
}

def process_statement(statement):
    statement = contractions.fix(statement)
    statement = statement.lower()
    statement = "".join([w for w in statement if w not in string.punctuation])
    #print(statement)
    return statement

def tag_statement(statement):
    sentiment = sid.polarity_scores(statement).get('compound')
    statement = nlp(statement)
    best_tag = "none",
    best_score = 0
    for key, phrase_list in phrases.items():
        if not phrase_list:
            continue
        score = 0
        phrase_sent = phrase_list[1]
        if sentiment * phrase_sent < 0:
            continue
        for phrase in phrase_list[0]:
            tok_phrase = nlp(phrase)
            phrase_score = tok_phrase.similarity(statement)
            if phrase_score > score:
                score = phrase_score
            #print(tok_phrase,statement, phrase_score)
        if score > 0.7:
            if score > best_score:
                best_score = score
                best_tag = key
        
    return best_tag

def get_object(statement):
    output = ""
    for tok in nlp(statement):
        #print(tok.dep_)
        if tok.dep_ == 'compound' or tok.dep_ == 'amod':
            output += tok.__str__() + " "
        elif tok.dep_ != 'dobj' and tok.dep_ != 'pobj':
            output = ""
        elif tok.dep_ == 'dobj' or tok.dep_ == 'pobj':
            return output + tok.__str__()
    if output == "":
        for tok in nlp(statement):
            if tok.dep_ == 'compound' or tok.dep_ == 'amod':
                output += tok.__str__() + " "
            elif tok.dep_ != 'nsubj':
                output = ""
            elif tok.dep_ == 'nsubj':
                return output + tok.__str__()
            
    return output
        
def get_attribute(statement):
    for tok in nlp(statement):
        if tok.dep_ == 'attr':
            return tok.__str__()
    return None
        
def get_response(tag, object):
    if tag == 'none':
        return random.choice(responses.get(tag))
    
    if tag == 'neutral':
        return random.choice(responses.get(tag))
    
    if tag == 'hello':
        return random.choice(responses.get(tag))
    
    if tag == 'goodbye':
        print(random.choice(responses.get(tag)))
        exit()
    
    if tag == 'name':
        if object:
            if query_fact('name','X'):
                name = get_solutions('name')[0].get("X")
                print("I will now refer to you as {}".format(object))
                retract_fact('name',name)
            assert_fact('name',object)
            object = object.capitalize()
            return random.choice(responses.get(tag)).format(object)
        else:
            return "Hello!"
    
    if tag == 'like':
        if query_fact('dislike', object):
            print("I guess you changed your mind then...")
            retract_fact('dislike', object)
        
        if not query_fact('like',object):
            assert_fact('like',object)
        return random.choice(responses.get(tag)).format(object)
    
    if tag == 'dislike':
        if query_fact('like', object):
            print("I guess you changed your mind then...")
            retract_fact('like', object)
        if not query_fact('dislike',object):
            assert_fact('dislike',object)
        return random.choice(responses.get(tag))
    
    if tag == 'ask_ingredient':
        object = object.capitalize()
        return random.choice(responses.get(tag)).format(object, "test_pie")
    
    if tag == 'get_ingredients':
        object = object.capitalize()
        return random.choice(responses.get(tag)).format(object, "test_ingredients")
    
    if tag == 'recommend':
        return random.choice(responses.get(tag)).format("test_pie")
    
    if tag == 'bake_time':
        object = object.capitalize()
        return random.choice(responses.get(tag)).format(object, "test_time", "test_temp")
    


    
def assert_fact(tag, object):
    object.replace(' ','-')
    fact_str = tag + "("+object+")"
    pl.assertz(fact_str)
    facts.append(fact_str)
    
def retract_fact(tag, object):
    object.replace(' ','-')
    fact_str = tag + "("+object+")"
    pl.retract(fact_str)
    facts.remove(fact_str)
    
def get_solutions(tag):
    query_str = tag+"(X)."
    sol = list(pl.query(query_str))
    return sol

def query_fact(tag, object):
    try:
        object.replace(' ','_')
        fact_str = tag + "("+object+")"
        sol = list(pl.query(fact_str))
        if sol:
            return True
        return False
    except:
        return False
    

# initialization
print("Hi! I'm piebot! You can ask me various things about pie recipes, as well as ask for recommendations!")
       
# main loop
while(1):  
    statement = input(">> ")
    if not statement:
        continue
    statement = process_statement(statement)
    dobj = get_object(statement)
    attr = get_attribute(statement)
    tag = 'none'
    if dobj:
        tag = tag_statement(statement.replace(dobj, "_"))
    else:
        tag = tag_statement(statement)
    if tag == 'name':
        print(get_response(tag, attr))
    else:
        print(get_response(tag, dobj))
    print(facts)
    
    
#       tag sentences
#       respond from kb
# store any personal information in pyswip
# web scrape for information