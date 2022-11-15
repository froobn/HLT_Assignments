import math
import pandas as pd
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import BernoulliNB
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier

df = pd.read_csv('Author Attribution/federalist.csv')

# STEP 1
print(df.head())
authors = {}
for row in df['author']:
    if authors.get(row) != None:
        authors[row] += 1
    else:
        authors[row] = 0
print(authors)

# STEP 2
stopwords = stopwords.words('english')

df['text_nostop'] = df['text'].apply(lambda words: ' '.join([word for word in words.split() if word not in stopwords]))
X_train, X_test, y_train, y_test = train_test_split(df['text_nostop'], df['author'], test_size=0.2, random_state=1234)
print(X_train.shape)
print(X_test.shape)

# STEP 3
tfidf = TfidfVectorizer()
X_train = tfidf.fit_transform(X_train) # fit the training data
X_test = tfidf.transform(X_test)
print(X_train.shape)
print(X_test.shape)

# STEP 4
bern = BernoulliNB()
bern.fit(X_train,y_train)
pred = bern.predict(X_test)
print("bernoulli: ", bern.score(X_test,y_test))

# STEP 5
X_train, X_test, y_train, y_test = train_test_split(df['text_nostop'], df['author'], test_size=0.2, random_state=1234)
tfidf = TfidfVectorizer(max_features=1000, min_df=2, max_df=0.5, ngram_range=(1, 2))
X_train = tfidf.fit_transform(X_train) # fit the training data
X_test = tfidf.transform(X_test)

bern = BernoulliNB()
bern.fit(X_train,y_train)
pred = bern.predict(X_test)
print("bernoulli: ", bern.score(X_test,y_test)) # MUCH BETTER RESULTS!

# STEP 6
lr = LogisticRegression(solver='liblinear') # CHANGED A TON OF PARAMETERS, COULD GET NO CHANGE
lr.fit(X_train,y_train)
pred = lr.predict(X_test)
print("logisitic regression: ", lr.score(X_test,y_test))

# STEP 7
mlp = MLPClassifier(max_iter=10000, hidden_layer_sizes=(7,9)) # about 82% accuracy
mlp.fit(X_train,y_train)
pred = mlp.predict(X_test)
print("MLP: ", mlp.score(X_test,y_test))