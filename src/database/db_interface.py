import logging
import os
import sqlite3
from typing import List, Tuple

from ..dataset.preprocessing import process_artist_row, process_track_row

log = logging.getLogger("db")


def connect_to_db(db_name: str) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    """Connects to the database and returns the connection and the cursor.

    Raises:
        Error: unknown error while connecting to the database

    Returns:
        Tuple[sqlite3.Connection, sqlite3.Cursor]: connection and cursor
    """
    db_path = os.getenv("DATA_PATH") + "\\databases\\binaries\\" + str(db_name) + ".db"

    if not os.path.exists(db_path):
        log.critical(
            f"Failed connecting to database '{db_name}': database does not exist"
        )
        exit(1)

    try:
        cnx = sqlite3.connect(db_path)
        cursor = cnx.cursor()
    except Exception as err:
        log.error(f"Failed connecting to database")
        raise err
    return (cnx, cursor)


def insert_track(row: List, cnx: sqlite3.Connection, cursor: sqlite3.Cursor):
    """Inserts a new track into the db.

    Args:
        row (List): list representing a read line of csv file
        cnx (sqlite3.Connection): the connection to the db
        cursor (sqlite3.Cursor): the cursor of the db

    Raises:
        Error: unknown error during sql query execution
    """
    processed_row = process_track_row(row)

    query = """
        INSERT INTO tracks 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    try:
        cursor.execute(query, processed_row)
        cnx.commit()
    except sqlite3.Error as err:
        log.error(f"Failed inserting track with name {row[1]}: {err}")
        cnx.rollback()
        raise err
    log.info(f"Inserted track with name {row[1]}")


def insert_song_status(status: List, cnx: sqlite3.Connection, cursor: sqlite3.Cursor):
    """Inserts a new status into the db.

    Args:
        status (List): row of tracks_status table
        cnx (sqlite3.Connection): the connection to the db
        cursor (sqlite3.Cursor): the cursor of the db

    Raises:
        Error: unknown error during sql query execution
    """

    query = """
        INSERT INTO track_status
        VALUES (?, ?, ?, ?);
    """
    try:
        cursor.execute(query, status)
        cnx.commit()
    except sqlite3.Error as err:
        log.error(f"Failed inserting track with song id {status[0]}: {err}")
        cnx.rollback()
        raise err
    log.info(f"Inserted track with id {status[0]}")


def update_song_status(
    cnx: sqlite3.Connection,
    cursor: sqlite3.Cursor,
    song_id: str,
    lyrics_skipped: bool = -1,
    lyrics_stored: bool = -1,
):
    """Updates either lyrics_skipped or lyrics_stored, if provided. Defaults skips both.

    Args:
        song_id (str): id of the song
        lyrics_skipped (bool): set to 1 if lyrics were skipped
        lyrics_stored (bool): set to 1 if lyrics were stored
        row (List): list representing a read line of csv file
        cnx (sqlite3.Connection): the connection to the db
        cursor (sqlite3.Cursor): the cursor of the db
    """
    query_skipped = f"""
        UPDATE track_status
        SET lyrics_skipped = {lyrics_skipped}
        WHERE song_id == "{song_id}";
    """

    query_stored = f"""
        UPDATE track_status
        SET lyrics_stored = {lyrics_stored}
        WHERE song_id == "{song_id}";
    """

    if lyrics_skipped != -1:
        try:
            cursor.execute(query_skipped)
            cnx.commit()
        except sqlite3.Error as err:
            log.error(f"Failed updating track status with song id {song_id}: {err}")
            cnx.rollback()
            # TODO raise err
        log.info(f"Updated track status with id {song_id}")

    if lyrics_stored != -1:
        try:
            cursor.execute(query_stored)
            cnx.commit()
        except sqlite3.Error as err:
            log.error(f"Failed updating track status with song id {song_id}: {err}")
            cnx.rollback()
            # TODO raise err
        log.info(f"Updated track status with id {song_id}")


def insert_artist(row: List, cnx: sqlite3.Connection, cursor: sqlite3.Cursor):
    """Inserts a new artist and if necessary new genres into the db.

    Args:
        row (List): list representing a read line of csv file
        cnx (sqlite3.Connection): the connection to the db
        cursor (sqlite3.Cursor): the cursor of the db

    Raises:
        Error: unknown error during sql query execution
    """
    processed_row, genres = process_artist_row(row)

    query = """
        INSERT INTO artists 
        VALUES (?, ?, ?, ?);
    """

    try:
        cursor.execute(query, processed_row)
        cnx.commit()
    except sqlite3.Error as err:
        log.error(f"Failed inserting artist with name {row[2]}: {err}")
        cnx.rollback()
        raise err
    log.info(f"Inserted artist with name {row[2]}")

    # insert genres
    insert_genres(genres, cnx, cursor)

    # insert artist-genres mappings
    insert_artist_genres(processed_row[0], genres, cnx, cursor)


def insert_genres(genres: List[str], cnx: sqlite3.Connection, cursor: sqlite3.Cursor):
    """Inserts genres into db if not existing.

    Args:
        genres (List[str]): list of genres
        cnx (sqlite3.Connection): the connection to the db
        cursor (sqlite3.Cursor): the cursor of the db

    Raises:
        Error: unknown error during sql query execution
    """
    # check if list of genres is empty
    if not genres:
        return

    query_exist = """
        SELECT * FROM genres AS g
        WHERE g.name == (?);
    """

    query_insert = """
        INSERT INTO genres
        VALUES(?);
    """

    for g in genres:
        # check if genre exists
        try:
            cursor.execute(query_exist, [g])
            genre_exists = True if cursor.fetchall() else False
        except sqlite3.Error as err:
            log.error(f"Failed querying genre {g}: {err}")
            raise err

        # if genre does NOT exists, add to table
        if not genre_exists:
            try:
                cursor.execute(query_insert, [g])
                cnx.commit()
            except sqlite3.Error as err:
                log.error(f"Failed inserting genre {g}: {err}")
                cnx.rollback()
                raise err
        else:
            log.info(f"Inserted genre {g}")


def insert_artist_genres(
    song_artist_id: str,
    genres: List[str],
    cnx: sqlite3.Connection,
    cursor: sqlite3.Cursor,
):

    query = """
        INSERT INTO artist_genres
        VALUES(?, ?);
    """

    for g in genres:
        try:
            cursor.execute(query, (song_artist_id, g))
            cnx.commit()
            log.info(f"Inserted ({song_artist_id}, {g})")
        except sqlite3.Error as err:
            log.error(f"Failed inserting ({song_artist_id}, {g}): {err}")
            cnx.rollback()
            continue


def insert_lyric_scores(
    song_id: str,
    lyric_scores: List[float],
    cnx: sqlite3.Connection,
    cursor: sqlite3.Cursor,
):
    query = """
        INSERT INTO lyric_scores
        VALUES(?, ?, ?, ?);
    """

    if len(lyric_scores) != 3:
        log.error("Skip lyric_scores: length does not equal 3.")
        return

    try:
        cursor.execute(query, [song_id] + lyric_scores)
        cnx.commit()
        log.info(f"Inserted lyrics scores for song {song_id}")
    except sqlite3.Error as err:
        log.error(f"Failed inserting lyrics scores for song {song_id}: {err}")
        cnx.rollback()
        raise err
