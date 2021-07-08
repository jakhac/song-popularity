import src.database.db_interface as db
import pandas as pd

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


def get_artist_df():
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


def get_lyric_df():
    """Loads the lyrical features from the database into a dataframe.

    Returns:
        dataframe: the pd dataframe of the lyrical features
    """
    cnx, cursor = db.connect_to_db("spotify_ds")

    query = """
        SELECT ls.word_count, ls.diversity, ls.repetition, t.popularity
        FROM lyric_scores AS ls
        INNER JOIN tracks AS t on t.id = ls.song_id;
    """

    return pd.read_sql_query(query, cnx)


# get music df
def get_music_df():
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

    return pd.read_sql_query(query, cnx)


def encode_genres(genre: str) -> int:
    new_genre = 17

    for g in meta_genres:
        if meta_genres[g] in genre:
            new_genre = g
            break

    return new_genre


# sample_distribution
