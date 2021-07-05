from typing import List

import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame
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

meta_genres = [
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

    df = pd.read_sql_query(query, cnx)

    return df


# def create_classes(popularities: List[int]) -> List[int]:
#     """Scale popularity into classes in [0, 10].

#     Args:
#         popularities (List[int]): List of popularity scores in [0, 100]

#     Returns:
#         List[int]: List of popularity scores in [0, 10]
#     """

#     return [int(x / 10) for x in popularities]


# def create_genre_classes(df: DataFrame) -> DataFrame:
#     """Put classes in meta genres.

#     Args:
#         df (DataFrame): DataFrame of artists

#     Returns:
#         df (DataFrame): DataFrame of artists
#     """
#     for index, row in df.iterrows():

#         # check if genre can be classified by meta genre
#         new_genre = "other"
#         for g in meta_genres:
#             if g in row[0]:
#                 new_genre = g
#                 break

#         df.at[index, "genre_name"] = new_genre

#     return df


def apply_genres(genre: List[int]) -> List[int]:
    new_genre = "other"

    for g in meta_genres:
        if g in genre:
            new_genre = g
            break

    return new_genre


def train_artists():
    """Train artists dataset."""

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

    print(X_train)
    print(y_train)

    # print(X_train.shape)
    # print(X_test.shape)

    return
