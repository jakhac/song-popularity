import logging
import os
import sqlite3

log = logging.getLogger("db")


cnx = None
cursor = None

TABLES = {}
TABLES[
    "artists"
] = """CREATE TABLE artists 
    (
        id TEXT NOT NULL,
        followers REAL,
        name TEXT,
        popularity INTEGER,
        PRIMARY KEY (id)
    );
    """

TABLES[
    "tracks"
] = """CREATE TABLE tracks
    (
        id TEXT,
        name TEXT,
        popularity INTEGER,
        duration_ms INTEGER,
        explict INTEGER,
        primary_artist_id TEXT, 
        release_year INTEGER,
        danceability REAL,
        energy REAL,
        key INTEGER,
        loadness REAL,
        mode INTEGER,
        speechiness REAL,
        acousticness REAL,
        instrumentalness REAL,
        liveness REAL,
        valence REAL,
        tempo REAL,
        time_signature INTEGER,
        PRIMARY KEY (id, primary_artist_id),
        FOREIGN KEY (primary_artist_id) REFERENCES artists(id)
    );
    """
TABLES[
    "genres"
] = """CREATE TABLE genres 
    (
        name TEXT,
        PRIMARY KEY (name)
    );
    """

TABLES[
    "artist_genres"
] = """CREATE TABLE artist_genres 
    (
        artist_id TEXT NOT NULL,
        genre_name TEXT NOT NULL,
        PRIMARY KEY (artist_id, genre_name),
        FOREIGN KEY (artist_id) REFERENCES artists(id),
        FOREIGN KEY (genre_name) REFERENCES genres(name)
    );
    """

TABLES[
    "lyric_scores"
] = """CREATE TABLE lyric_scores 
    (
        song_id TEXT,
        word_count INT,
        diversity REAL,
        repition REAL,
        PRIMARY KEY (song_id),
        FOREIGN KEY (song_id) REFERENCES tracks(id)
    );
    """


def create_db(db_name: str):
    """Creates a new database with the specified name if not exists.

    Args:
        db_name (str): the name of the database
    """
    global cnx, cursor

    if db_name is None:
        log.critical(f"Failed creating database: db_name is None")
        exit(1)

    db_path = os.getenv("DATA_PATH") + "\\databases\\binaries\\" + db_name + ".db"

    # check if db already exists
    if os.path.exists(db_path):
        log.info(f"Already existing database {db_name}")
        return
    elif not os.path.exists(os.path.dirname(db_path)):
        # create dirs on path if not exist
        os.makedirs(os.path.dirname(db_path))

    cnx = sqlite3.connect(db_path)
    if cnx is None:
        log.critical(f"Failed connecting to database {db_name}")
        exit(1)

    # enable foreign keys
    try:
        cnx.execute("PRAGMA foreign_keys = 1;")
        log.info(f"Enabled foreign keys for database {db_name}")
    except Exception as err:
        log.warn(f"Failed enabling foreign keys for database {db_name}: {err}")

    cursor = cnx.cursor()

    # create tables
    for table in TABLES:
        cursor.execute(TABLES[table])
        log.info(f"Created table {table}")

    cnx.commit()
    log.info(f"Created database {db_name}")
