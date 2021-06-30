import json
import logging
import logging.config
import os
import sqlite3
from typing import List
from datetime import datetime
import signal
import sys

import lyricsgenius as api
from pathlib import Path

from ..database import db_interface as db
from ..dataset.preprocessing import content_is_lyrics, valid_lyrics, clean_lyrics


from dotenv import load_dotenv

load_dotenv()

LYRICS_PATH = Path(os.getenv("DATA_PATH")) / "datasets" / "lyrics"

log = logging.getLogger("lyrics")

genius = None
lyrics_dict = {}


def connect_to_api() -> None:
    """Access Genius API via access token and declare instance of Genius class."""
    global genius
    log.info("Connecting to Genius API...")
    try:
        genius = api.Genius(os.getenv("GENIUS_ACCESS_TOKEN"), verbose=False)
    except Exception as err:
        log.critical(f"Failed connecting to Genius API: {err}")
        log.info("Exiting...")
        exit(1)
    log.info("Connected to Genius API")


def get_song_lyrics(song_title: str, artist: str) -> str:
    """Gets the lyrics of the specified song fo the specified artist.

    Args:
        song_title (str): the title of the song
        artist (str): the artist of the song

    Raises:
        Exception: unknown exception occured

    Returns:
        lyrics (str): the lyrics of the song
    """
    # get song object from genius
    try:
        song = genius.search_song(song_title, artist)
    except Exception as err:
        log.warning(f"Failed getting object for song {song_title}: {err}")
        raise err

    # get lyrics from song object
    try:
        lyrics = song.lyrics
    except Exception as err:
        log.warning(f"Failed getting lyrics for song {song_title}: {err}")
        raise err
    return lyrics


def store_song_lyrics_in_dict(song_id: str, lyrics: str) -> None:
    """Stores the song with its artist and lyrics in the dict.

    Args:
        song_id (str): the id of the song
        lyrics (str): the lyrics of the song
    """
    # create entry for song and lyrics
    if song_id not in lyrics_dict:
        lyrics_dict[song_id] = lyrics
        log.info(f"Stored lyrics of song with id {song_id} in dict")
    else:
        log.info(f"Skipping already stored lyrics of song with id {song_id}")


def lyrics_dict_to_json(file_name: str) -> None:
    """Saves the lyrics_dict as a .json file.

    Args:
        file_name (str): name of the json file
    """
    if file_name is None:
        log.error(f"Unspecified file name of lyrics.json")
        return

    # path to target json
    lyrics_json_path = (
        os.getenv("DATA_PATH") + "\\datasets\\lyrics\\lyrics_" + file_name + ".json"
    )

    if not os.path.exists(os.path.dirname(lyrics_json_path)):
        os.makedirs(os.path.dirname(lyrics_json_path))

    # write dict into file
    with open(lyrics_json_path, "a", encoding="utf-8") as lyrics_json:
        json.dump(lyrics_dict, lyrics_json, ensure_ascii=False, indent=4)

        log.info(
            f"Stored lyrics_dict with {len(lyrics_dict)} songs in file at {lyrics_json_path}"
        )


def store_lyrics_to_txt(song_id: str, lyrics: str):
    """Saves the lyrics in .txt file, if not exists. Filename is song_id.

    Args:
        song_id (str): song_id, used as name of the json file
        lyrics (str): lyrics of song to store
    """

    # This lyrics path does not exist, only non-stored songs searched
    lyrics_path = os.getenv("DATA_PATH") + "\\datasets\\lyrics\\" + song_id + ".txt"

    # write lyrics into file
    with open(lyrics_path, "a", encoding="utf-8") as file:
        file.write(lyrics)

    # log.info(f"Stored lyrics of song_id {song_id}")


def get_song_list(cnx: sqlite3.Connection, cursor: sqlite3.Cursor) -> List[List[str]]:
    """Query db and return for list of (song_id, song_name, song_artist) tuples.

    Args:
        cnx (sqlite3.Connection): the connection to the db
        cursor (sqlite3.Cursor): the cursor of the db

    Raises:
        Error: unknown error during sql query execution
    """

    query = """
        SELECT t.id, t.name, a.name
        FROM tracks AS t
        INNER JOIN artists AS a ON t.primary_artist_id == a.id
        INNER JOIN track_status AS ts ON t.id == ts.song_id
        WHERE ts.song_valid == 1
        AND ts.lyrics_skipped == 0
        AND ts.lyrics_stored == 0
        AND t.release_year >= 2019;
    """

    try:
        cursor.execute(query)
        results = cursor.fetchall()
    except sqlite3.Error as err:
        log.error(f"Failed to query all songs in table tracks: {err}")
        raise err
    return results


def get_unscored_songs(cnx: sqlite3.Connection, cursor: sqlite3.Cursor) -> List[str]:
    """Query db and return for list of (song_id, song_name, song_artist) tuples,
    which are not scored in lyric_scores yet.

    Args:
        cnx (sqlite3.Connection): the connection to the db
        cursor (sqlite3.Cursor): the cursor of the db

    Raises:
        Error: unknown error during sql query execution

    Return:
        List[str]: list of song ids
    """

    query = """
        SELECT ts.song_id
        FROM track_status AS ts
        LEFT JOIN lyric_scores AS ls ON ls.song_id = ts.song_id
        WHERE ls.song_id IS NULL 
        AND ts.song_valid == 1
        AND ts.lyrics_stored == 1;
    """

    try:
        cursor.execute(query)
        results = list(map(lambda x: x[0], cursor.fetchall()))
    except sqlite3.Error as err:
        log.error(f"Failed to query all songs in table tracks: {err}")
        raise err
    return results


def run_lyrics_getter() -> None:
    """Get lyrics for all tracks in spotfiy_ds and store them in .txt file."""

    connect_to_api()
    cnx, cursor = db.connect_to_db("spotify_ds")

    # query db to get list of all (song_id, song_name, artist) tuples
    song_list = get_song_list(cnx, cursor)
    len_songs = len(song_list)

    for i in range(0, len(song_list)):

        if i % 100 == 0:
            log.info(f"Song: {i}/{len_songs}")

        try:
            lyrics = get_song_lyrics(song_list[i][1], song_list[i][2])
        except Exception:
            log.warning(f"Skipping song {song_list[i][1]}, no lyrics found.")
            db.update_song_status(cnx, cursor, song_list[i][0], lyrics_skipped=1)
            continue

        if not valid_lyrics(lyrics):
            log.warning(f"Skipping song {song_list[i][1]}: invalid lyrics")
            db.update_song_status(cnx, cursor, song_list[i][0], lyrics_skipped=1)
            continue

        lyrics = clean_lyrics(lyrics)

        log.info(f"Store lyrics for song_id {song_list[i][0]} ({song_list[i][1]}).")

        store_lyrics_to_txt(song_list[i][0], lyrics)
        db.update_song_status(cnx, cursor, song_list[i][0], lyrics_stored=1)

    log.info("Finished lyrics scraping.")


def get_lyrics_from_file(song_id: str) -> str:
    """Get lyrics for song_id from dataset folder.

    Args:
        song_id (str): id of the song

    Raises:
        Exception: error while opening/reading file

    Returns:
        (str): lyrics of song
    """
    lyrics_file_path = LYRICS_PATH / (song_id + ".txt")

    with open(lyrics_file_path, "r", encoding="utf-8") as f:
        lyrics = f.read()

    if lyrics is not None:
        return lyrics
    else:
        raise Exception(f"Failed reading lyrics file for song {song_id}")
