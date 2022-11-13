# Written by Bill Dozier and Josh Olowoyeye


import json
import os
import pickle
import re
import requests
from bs4 import BeautifulSoup
from nltk import sent_tokenize
from nltk.corpus import stopwords
import nltk

site = 'https://www.google.com/search?q=pie'

def crawl_topic(topic_url, topic):
    site = requests.get(topic_url) 

    soup = BeautifulSoup(site.content, "html.parser")

    for script in soup(["script", "style"]):
        script.extract()

    url_list = []
    for link in soup.find_all('a'):
        if len(url_list) >= 15:
            return url_list
        link_str = str(link.get('href'))
        if link_str.startswith('/url?q='):
            link_str = link_str[7:]
        if link_str.startswith('http') and 'search' not in link_str and 'google' not in link_str:
            print(link_str)
            url_list.append(link_str)

def output_html(url_list):
    count = 0
    for url in url_list:
        site = requests.get(url)
        soup = BeautifulSoup(site.content)
        data = soup.findAll(text=True)
        result = filter(visible, data)
        temp_list = list(result)      # list from filter
        temp_str = ' '.join(temp_list)
        file = open('Web Crawler/htmldata/site'+str(count)+'.txt', 'w+',encoding="utf-8")
        file.write(temp_str)
        file.close()
        count+=1

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True      

def clean_file(file_path):
     with open('Web Crawler/htmldata/'+file_path, 'r',encoding="utf-8") as file:
        file_text = ' '.join(file.read().split())
        file_text = re.sub(r'[^A-Za-z0-9.,!?\'\"-()]+', ' ', file_text)
        tokens = sent_tokenize(file_text)
        with open('Web Crawler/sentdata/'+file_path, 'w+') as file:
            for sentence in tokens:
                file.write(sentence + "\n")

def get_important_terms():
    stop_words = stopwords.words('english')
    all_words = []
    for filename in os.listdir('Web Crawler/sentdata/'):
        f = os.path.join('Web Crawler/sentdata/', filename)
        # checking if it is a file
        if os.path.isfile(f):
            with open(f,'r',encoding="utf-8") as file:
                
                cleaned = file.read().lower()
                cleaned = re.sub(r'[^A-Za-z0-9\'-]+', ' ', cleaned)
                word_list = cleaned.split()
                for word in word_list:
                    if word not in stop_words:
                        all_words.append(word)
    
    freq_dist = nltk.FreqDist(all_words)
    top_words = sorted(freq_dist.items(), key=lambda item: item[1], reverse=True)[:60]    
    print(top_words)

url_list = crawl_topic(site, 'pie')
output_html(url_list)

for i in range(15):
   clean_file('site'+str(i)+'.txt')
get_important_terms()


word_dict = {
    'pie': [
            "There's a town called Pie Town in New Mexico, USA",

            "Pies can be traced back to 6000 BC",	

            "The first pie recipe was published by the Romans"
        ],

    'chocolate': [
            "Chocolate is a common filling or topping for pies",
	
            "It takes 400 cocoa beans to make one pound of chocolate",

            "Chocolate comes from a fruit tree; it's made from a seed"
        ],

    'food': [
        "Food is any substance consumed to provide nutritional support for an organism",

        "Pie is a delicious desert food that is part of cuisine all around the world",

        "Food usually needs to go through some steps for proper preparation before being eaten, whether that is baking, frying, or grilling, there are many common ways of preparing food for consumption"
        ],

    'kitchen': [
            "A kitchen is a room or part of a room used for cooking and food preparation in a dwelling or in a commercial establishment.",

            "The main functions of a kitchen are to store, prepare and cook food.",

            "The kitchen houses many common appliances like a refrigerator, freezer, microwave oven, convection oven, and sink."

        ],

    'pizza': [
            "Pizza is a dish of Italian origin consisting of a usually round, flat base of leavened wheat-based dough topped with tomatoes, cheese, and often various other ingredients",

            "There are many disputes over what toppings are right to put on a pizza, the most notable of which is the pineapple wedge.",

            "A small pizza is sometimes called a pizzetta and person who makes pizza is known as a pizzaiolo."
        ],

    'recipes': [
            "A recipe is a set of instructions that describes how to prepare or make something, especially a dish of prepared food.",

	        "The earliest known written recipes date to 1730 BC and were recorded on cuneiform tablets found in Mesopotamia.",

            "The internet is a great source for recipes for any dish ones heart desires; there are countless recipes available at just the click of a mouse thanks to the internet."
        ],

    'oven': [
            "The heat source of ovens can be generated using coal, iron, wood, gas, microwaves, or, most commonly, electricity."

            "In recent times, there has been a resurgence of wood-fired ovens that are either purchased or made, and they are generally situated in outdoor living areas and are used to cook pizzas and baked goods."

            "The hottest part of an oven is the top."
        ],

    'cookies': [
            "Americans consume over 2 billion cookies a year … about 300 cookies for each person.",

            "95.2 percent of U.S. households consume cookies.",

            "Half the cookies baked in American homes each year are chocolate chip."
        ],

    'butter': [
            "Butter is a dairy product made from the fat and protein components of churned cream",

            "Scandinavia has the oldest tradition in Europe of butter export trade, dating at least to the 12th century.",

            "the earliest milk production would have been from sheep or goat's milk in the area of Iran and Iraq around 9,000 to 8,000 BCE and butter would have soon been found naturally in milk containers"
        ],

    'cream': [
            "Cream is a dairy product composed of the higher-fat layer skimmed from the top of milk before homogenization"

            "Cream is used as an ingredient in many foods, including ice cream, many sauces, soups, stews, puddings, and some custard bases, and is also used for cakes."

            "Cream (usually light/single cream or half and half) may be added to coffee."
        ]
}
    
with open('Web Crawler/knowledge-base.p', 'wb') as file:
    pickle.dump(word_dict, file)


