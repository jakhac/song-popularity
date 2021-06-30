from typing import List

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# import metrics
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

# import models
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from ..database import db_interface as db


def load_data():
    """Loads the musical features from the database into a dataframe

    Returns:
        dataframe: the pd dataframe of the musical features
    """
    cnx, cursor = db.connect_to_db("spotify_ds")

    query = """
        SELECT t.duration_ms, t.explict, t.release_year, t.danceability, t.energy, t.key, t.loadness, t.mode, t.speechiness, t.acousticness, t.instrumentalness, t.liveness, t.valence, t.tempo, t.time_signature, t.popularity
        FROM tracks AS t
        INNER JOIN track_status AS ts
        ON t.id == ts.song_id
        WHERE ts.song_valid == 1
        AND ts.lyrics_stored == 1
        AND t.release_year >= 2000;
    """

    df = pd.read_sql_query(query, cnx)

    return df


def create_classes(popularities: List[int]) -> List[int]:
    """Scale popularity into classes in [0, 10].

    Args:
        popularities (List[int]): List of popularity scores in [0, 100]

    Returns:
        List[int]: List of popularity scores in [0, 10]
    """

    return [int(x / 10) for x in popularities]


def train():
    df = load_data()

    X = df.values[:, :15]
    y = create_classes(df.values[:, 15])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(X_train.shape)
    print(X_test.shape)

    # clf = MLPClassifier(hidden_layer_sizes=(100, 100, 100))
    # clf.fit(X_train, y_train)
    # print(clf.predict(X_test)[:5])
    # print(y_test[:5])

    # y_predict = clf.predict(X_test)

    # print(round(accuracy_score(y_test, y_predict), 4))

    # store each model with: name, function
    models = [
        {"name": "Gaussian Naive Bayes", "function": GaussianNB},
        {"name": "Neural Network", "function": MLPClassifier},
        {"name": "Decision Trees", "function": DecisionTreeClassifier},
        {"name": "Random Forest", "function": RandomForestClassifier},
        {"name": "SVC", "function": SVC},
        {"name": "KNeighborsClassifier", "function": KNeighborsClassifier},
    ]

    # use each model and calculate accuracy
    for model in models:
        print("Using " + model["name"])
        clf = model["function"]()

        # fit the model
        clf.fit(X_train, y_train)

        # predict on test set
        y_predict = clf.predict(X_test)
        print("Accuracy: " + str(round(accuracy_score(y_test, y_predict), 4)))

    # use different number of trees in forest (comparing different hyperparameters)
    # forest_size = [10, 50, 100, 200, 1000]
    forest_size = [10]

    # set seed for random state to get compareable results in every execution (forest randomness)
    np.random.seed(500)

    # store metrics with: name, function, parameters
    metrics = [
        ("Accuracy: ", accuracy_score, {"y_true": y_test, "y_pred": y_predict}),
        (
            "F1: ",
            f1_score,
            {"y_true": y_test, "y_pred": y_predict, "average": "micro"},
        ),
        (
            "Precision: ",
            precision_score,
            {"y_true": y_test, "y_pred": y_predict, "average": "micro"},
        ),
        (
            "Recall:",
            recall_score,
            {"y_true": y_test, "y_pred": y_predict, "average": "micro"},
        ),
    ]

    for trees in forest_size:
        # set forest size
        print("Predicting with forest size " + str(trees))
        rf = RandomForestClassifier(n_estimators=trees)

        # fit the model
        rf.fit(X_train, y_train)

        # predict on test set
        y_predict = rf.predict(X_test)

        # calculate and print metrics
        list(
            map(
                lambda metric: print(metric[0] + str(round(metric[1](**metric[2]), 4))),
                metrics,
            )
        )
        print("--------\n")
