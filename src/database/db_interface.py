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


def insert_lyric_scores(lyric_scores: List[str], cursor: sqlite3.Cursor):
    pass
