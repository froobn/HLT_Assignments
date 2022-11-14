import json
import pickle
import random
import requests
import spacy
from pyswip import Prolog
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.stem import WordNetLemmatizer
import contractions
import string

# LIBRARIES
# spacy, pyswip, contractions, nltk

lemmatizer = WordNetLemmatizer()
sid = SentimentIntensityAnalyzer()
nlp = spacy.load("en_core_web_md")
pl = Prolog()
facts = []
recipes = {}

sample_pies = [
    'apple pie',
    'cherry pie',
    'pumpkin pie',
    'pecan pie',
    'chocolate pie',
    'blueberry pie',
    'key lime pie',
    'peanut butter pie',
    'lemon meringue pie',
    'banana cream pie'
]

phrases = {
    "none": [],
    "ask_name": [["what is your name", "what is your _", "what do i call you"],0],
    "thank": [["thank you", "thank you piebot", "thank _"],0],
    "hello": [['hello','greetings','hi', 'salutations', 'hi _bot' ,'hello _bot'], 0],
    "goodbye": [['goodbye','bye','talk to you later', 'goodbye _bot'],0],
    "name": [['my name is _', 'I am named _', 'You can call me _'], 0],
    "neutral": [["_ is alright, _ is not bad", "I do not hate _", "_ is not the worst", "_ is okay"], 0],
    "like": [["i like _", "_ is tasty", "_ is good", "i am a fan of _", "i love _"], 1],
    "dislike": [["i don't like _", "i dislike _", "i hate _", "_ is horrible", "_ is nasty", "_ is the worst", "_ is not good", "_ is not tasty", "i am not a fan of _"], -1],
    "ask_ingredient": [["what kind of pie uses _", "which pies have _ in them","What pies use _"],0],
    "get_ingredients": [["what ingredients are in _", "what is used in _", "what do i need to make _"], 0],
    "recommend": [["what is your recommendation","what do you recommend?","recommend me a pie", "what is a pie i might like", "find me a pie i would like"],0],
    "prepare_time": [["how long does _ take to make", "how long to make _", "how long until i can eat _"],0],
    "get_recipe": [["what is the recipe for _","find me a recipe for _", "can you get me a recipe for _", "search for recipes for _"], 0]
}

responses = {
    "none": ["I don't quite understand.", "I don't think I understood that."],
    "ask_name": ['My name is PieBot!'],
    "thank": ["My pleasure!", "No problem!", "The pleasure is mine!"],
    "hello": ["Hello!", "Hi there!","Salutations fellow pie enjoyer!"],
    "goodbye": ["Goodbye!", "It was nice talking with you!"],
    "name": ["Hello {}!", "Nice to meet you, {}!", "Hi {}!"],
    "neutral": ["That's understandable."],
    "like": ["Isn't {} great!", "{} is pretty popular, isn't it!"],
    "dislike": ["I know a lot of people that feel the same way.", "Yeah I'm not the biggest fan either."],
    "ask_ingredient": ["{} is in the recipe for:\n{}"],
    "get_ingredients": ["{} contains the following:\n{}"],
    "recommend": ["I think you would like:\n{}"],
    "prepare_time": ["{} takes {} minutes to prepare."],
    "get_recipe": ["here is your recipe: {}"]
}

def process_statement(statement):
    '''
        splits contractions into their seperate forms and removes punctuation
    '''
    statement = contractions.fix(statement)
    statement = "".join([w for w in statement if w not in string.punctuation])
    return statement

def tag_statement(statement):
    '''
        tags a sentence as one of the phrases from the variable phrases,
        
        primarily based on the sentence that is closest to any given phrase tag's sample sentences, and throws out any phrase tags that would have opposite sentiment to the inputted statement. such as like vs dislike.
    '''
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
        if score > 0.7:
            if score > best_score:
                best_score = score
                best_tag = key
        
    return best_tag

def get_object(statement):
    '''
        attempts to retrieve the direct object, or in somecases the subject of a given sentence.
        sometimes certain sentences can be a little messy, like with the word pie, so there a few rules in place to manage and retrieve the best value to use for the response
    '''
    output = ""
    compounded = False
    for tok in nlp(statement):
        if tok.dep_ == 'compound' or tok.dep_ == 'amod':
            compounded = True
            output += tok.__str__() + " "
        elif tok.dep_ != 'dobj' and tok.dep_ != 'pobj':
            compounded = False
            output = ""
        elif (compounded and 'pie' in tok.text) or (tok.text != 'recipe' and tok.text != 'bake') and (tok.dep_ == 'dobj' or tok.dep_ == 'pobj') and not 'pie' in tok.text:
            return output + tok.__str__().lower()
    if output == "":
        for tok in nlp(statement):
            if tok.dep_ == 'compound' or tok.dep_ == 'amod':
                output += tok.__str__() + " "
            elif tok.dep_ != 'nsubj':
                output = ""
            elif tok.dep_ == 'nsubj':
                return output + tok.__str__().lower()
    if output == "":
        if 'pie' in statement:
            return "pie"
    output = lemmatizer.lemmatize(output)
    return output.lower()
        
def get_attribute(statement):
    '''
        retreives the first attr token from a statement, mainly used to extract names from a statement
    '''
    for tok in nlp(statement):
        if tok.dep_ == 'attr':
            return tok.__str__()
    return None
        
def get_response(tag, object):
    '''
        returns the response to a given tag and object, 
        tag comes from tag_statement(statement) and object comes from get_object(statement)
        an example is if the tag is 'name' and the object is 'Bill', a sample response would be: 'Hello Bill!'
    '''
    if tag == 'none' or tag == ('none',):
        return random.choice(responses.get('none'))
    
    if tag == 'neutral' or tag == 'hello' or tag == 'ask_name' or tag == 'thank' or tag == 'favorite':
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
        recipe_list = search_ingredient(object)
        object = object.capitalize()
        return random.choice(responses.get(tag)).format(object, recipe_list)
    
    if tag == 'get_ingredients':
        recipe = get_recipe(object)
        if not recipe:
            return
        ingredients = get_ingredients(recipe)
        object = object.capitalize()
        return random.choice(responses.get(tag)).format(object, ingredients) 
    
    if tag == 'recommend':
        recommendation = get_recommendation()
        if len(recommendation) == 0:
            return "I can't recommend anything if I don't know your likes or dislikes."
        rec_str = ""
        for rec in recommendation:
            rec_str += rec.get('label')+"\n"
        return random.choice(responses.get(tag)).format(rec_str)
    
    if tag == 'prepare_time':
        recipe = get_recipe(object)
        if not recipe:
            return
        object = object.capitalize()
        return random.choice(responses.get(tag)).format(object, recipe.get('totalTime'))
    
    if tag == 'get_recipe':
        recipe = get_recipe(object)
        if not recipe:
            return
        return random.choice(responses.get(tag)).format(recipe.get('url'))



def check_is_pie(recipe):
    '''
        simply checks if the word pie exists in a phrase, used for ensuring the bot restricts itself to pie recipes
    '''
    recipe = recipe.lower()
    if 'pie' in recipe:
        return True
    return False
    
def assert_fact(tag, object):
    '''
        connecting function for pySWIP, asserts a fact to the knowledge base, and adds it to the fact list for debugging purposes
    '''
    object = object.lower()
    object = object.replace(' ','-')
    fact_str = tag + "("+object+")"
    pl.assertz(fact_str)
    facts.append(fact_str)
    
def retract_fact(tag, object):
    '''
        connecting function for pySWIP, retracts a fact to the knowledge base, and removes it from the fact list for debugging purposes
    '''
    object = object.lower()
    object = object.replace(' ','-')
    fact_str = tag + "("+object+")"
    pl.retract(fact_str)
    facts.remove(fact_str)
    
def get_solutions(tag):
    '''
        connecting function for pySWIP, retrieves all solutions to a given phrase,
        an example being if tag == 'like' it will return everything the user likes
    '''
    try:
        query_str = tag+"(X)."
        sol = list(pl.query(query_str))
        return sol
    except:
        return []

def query_fact(tag, object):
    '''
        checks to see if a certain fact is true, based on the given tag and object
        prolog structure is: tag(object).
    '''
    try:
        object = object.replace(' ','_')
        fact_str = tag + "("+object+")"
        sol = list(pl.query(fact_str))
        if sol:
            return True
        return False
    except:
        return False
    
# RECIPE API METHODS

def get_likes():
    '''
        queries the prolog knowledge base for all the likes the user has inputted on runtime
    '''
    output = []
    solutions = get_solutions('like')
    for solution in solutions:
        for key,value in solution.items():
            output.append(value)
    return output

def get_dislikes():
    '''
        queries the prolog knowledge base for all the dislikes the user has inputted on runtime
    '''
    output = []
    solutions = get_solutions('dislike')
    for solution in solutions:
        for key,value in solution.items():
            output.append(value)
    return output
       
def get_recommendation():
    '''
        adds any loaded pies that contain ingredients the user has said they like to a list, and remove any pies that contain ingredients the user said they don't like
    '''
    output = []
    likes = get_likes()
    dislikes = get_dislikes()
    for key, recipe in recipes.items():
        for like in likes:
            if contains_ingredient(like, recipe):
                output.append(recipe)
        for dislike in dislikes:
            if recipe in output and contains_ingredient(dislike, recipe):
                output.remove(recipe)
    return output
        
def get_recipe(recipe):
    '''
        gets recipe data from the edemam API, returning the recipe with the closest name to the given recipe string
    '''
    if not check_is_pie(recipe):
        print("I don't think I've head of that pie...")
        return None
    if recipe in recipes.keys():
        return recipes[recipe]
    #appid = 'd04c6f39'
    #appkey = 'ad636405357cd0126ca040ca79306afb'
    url_recipe = recipe.replace(" ", "%20")
    url = "https://api.edamam.com/api/recipes/v2?type=public&q="+url_recipe+"&time=1%2B&app_id=d04c6f39&app_key=ad636405357cd0126ca040ca79306afb"
    recipe = recipe.lower()
    response = requests.get(url)
    response = json.loads(response.text)
    print('loading...')
    best_score = 0
    best_recipe = None
    for hit in response.get('hits'):
        hit_recipe = hit.get('recipe')
        hit_nlp = nlp(hit_recipe.get('label').lower())
        
        recipe_nlp = nlp(recipe)
        score = recipe_nlp.similarity(hit_nlp)
        if score > best_score:
            best_score = score
            best_recipe = hit_recipe
    recipes[recipe] = best_recipe
    store_recipes()
    return best_recipe

def search_ingredient(ingredient):
    '''
        searches all the loaded recipes for any recipes that contain a given ingredient
    '''
    output = ""
    for key, recipe in recipes.items():
        if contains_ingredient(ingredient, recipe):
            output += recipe.get('label')+"\n"
    return output

def get_ingredients(recipe):
    '''
        gets all the ingredients for a given recipe
    '''
    output = ""
    for ingredient in recipe.get('ingredients'):
        output += ingredient.get('food') + "\n"
    return output

def contains_ingredient(ingredient, recipe):
    '''
        checks if a given recipe contains a given ingredient, as well as checking if the ingredient is in the name of the recipe
    '''
    ingredients = get_ingredients(recipe)
    if ingredient in ingredients:
        return True
    if ingredient in recipe.get('label').lower():
        return True
    return False

def store_recipes():
    '''
        updates the pickle recipe file for the current recipes list
    '''
    recipe_file = open('ChatBot/recipes.pickle','wb')
    pickle.dump(recipes,recipe_file)
    recipe_file.close()

def load_recipes():
    '''
        loads the recipes stored in the pickle file
    '''
    try:
        recipe_file = open('ChatBot/recipes.pickle', 'rb')     
        output = pickle.load(recipe_file)
        return output
    except:
        return {}


# initialization
print("Hi! I'm piebot! I Come preloaded with some of the most popular pies!\nYou can ask me various things about pie recipes, as well as ask for recommendations!\nRemember to always ask and respond with full sentences!\nWhat's your name?")
recipes = load_recipes()
# for pie in sample_pies:
#     get_recipe(pie)

# main loop
'''
    main control loop, close on saying a phrase tagged as 'goodbye'
'''
while(1):  
    statement = input(">> ")
    if not statement:
        continue
    statement = process_statement(statement)
    dobj = get_object(statement)
    attr = get_attribute(statement)
    statement = statement.lower()
    tag = 'none'
    if dobj:
        tag = tag_statement(statement.replace(dobj, "_"))
    else:
        tag = tag_statement(statement)
    if tag == 'name':
        print(get_response(tag, attr))
    else:
        print(get_response(tag, dobj))
    