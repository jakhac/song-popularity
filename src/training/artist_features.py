#!/usr/bin/env python
# coding: utf-8

import os
import sys
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

DATA_PATH = Path(os.getenv("DATA_PATH"))

# only for .ipynb because relative imports don't work
root_path = DATA_PATH.parent
os.chdir(str(root_path))

import src.database.db_interface as db
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

# import models
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import OrdinalEncoder
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

meta_genres = dict(
    enumerate(
        [
            "alternative",
            "blues",
            "classical",
            "country",
            "dance",
            "electronic",
            "folk",
            "pop",
            "hip hop",
            "rap",
            "jazz",
            "latin",
            "r&b",
            "reggae",
            "rock",
            "metal",
            "world",
            "other",
        ]
    )
)
print(meta_genres)


def load_data():
    """Loads the artist features from the database into a dataframe

    Returns:
        dataframe: the pd dataframe of the artist features
    """
    cnx, cursor = db.connect_to_db("spotify_ds")

    query = """
        SELECT ag.genre_name, a.followers, a.popularity
        FROM artists AS a
        INNER JOIN artist_genres AS ag ON a.id == ag.artist_id
        INNER JOIN tracks AS t ON t.primary_artist_id == a.id
        INNER JOIN lyric_scores AS ls ON ls.song_id == t.id
        AND t.release_year >= 2000
        GROUP BY a.id;
    """

    return pd.read_sql_query(query, cnx)


def apply_genres(genre: str) -> int:
    new_genre = 17

    for g in meta_genres:
        if meta_genres[g] in genre:
            new_genre = g
            break

    return new_genre


def calculate_metrics(clf, X_test, y_test):
    # predict on test set
    y_predict = clf.predict(X_test)

    # print metrics
    print("Accuracy: " + str(round(accuracy_score(y_test, y_predict), 4)))
    print("F1: " + str(round(f1_score(y_test, y_predict, average="weighted"), 4)))
    print(
        "Recall: " + str(round(recall_score(y_test, y_predict, average="weighted"), 4))
    )
    print(
        "Precision: "
        + str(round(precision_score(y_test, y_predict, average="weighted"), 4))
    )
    print("\n")

    # check which labels do not appear in prediction
    print(f"Contained predictions: {set(y_predict)}")
    print(f"Contained tests: {set(y_test)}")
    set(y_test) - set(y_predict)


df = load_data()

# Scale followers to [0, 10]
max_followers = df["followers"].max()
df["followers"] = df["followers"].apply(lambda x: int(x / (max_followers / 10)))

# Use meta genres
df["genre_name"] = df["genre_name"].apply(apply_genres)

# Scale popularity
y = df["popularity"].apply(lambda x: int(x / 10))
X = df.values[:, :2]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(X_train.shape)
print(X_test.shape)
print(df)


print("Gaussian Naive Bayes")
gaussian_clf = GaussianNB()

# fit the model
gaussian_clf.fit(X_train, y_train)

calculate_metrics(gaussian_clf, X_test, y_test)


print("SVC")
svc_clf = SVC()

# fit the model
svc_clf.fit(X_train, y_train)

calculate_metrics(svc_clf, X_test, y_test)


# ## Neural Network


print("Neural Network")
nn_clf = MLPClassifier()

# fit the model
nn_clf.fit(X_train, y_train)

calculate_metrics(nn_clf, X_test, y_test)


print("K-Neighbours Classifier")
knn_clf = KNeighborsClassifier()

# fit the model
knn_clf.fit(X_train, y_train)

calculate_metrics(knn_clf, X_test, y_test)


print("Decision Trees")
dt_clf = DecisionTreeClassifier()

# fit the model
dt_clf.fit(X_train, y_train)

calculate_metrics(dt_clf, X_test, y_test)


# use different number of trees in forest (comparing different hyperparameters)
forest_size = [10, 20, 50, 100]

# set seed for random state to get compareable results in every execution (forest randomness)
np.random.seed(500)

for trees in forest_size:
    # set forest size
    print("Predicting with forest size " + str(trees))
    rf = RandomForestClassifier(n_estimators=trees)

    # fit the model
    rf.fit(X_train, y_train)

    calculate_metrics(rf, X_test, y_test)
    print("--------\n")
