import json
import logging
import logging.config
import os
import sqlite3
from typing import List

import lyricsgenius as api
from langdetect import detect

from ..database import db_interface as db
from ..dataset import lyrics_preprocessing as lp

log = logging.getLogger("lyrics")

genius = None
lyrics_dict = {}


def connect_to_api() -> None:
    """Access Genius API via access token and declare instance of Genius class."""
    global genius
    log.info("Connecting to Genius API...")
    try:
        genius = api.Genius(os.getenv("GENIUS_ACCESS_TOKEN"))
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
        log.error(f"Failed getting object for song {song_title}: {err}")
        raise err

    # get lyrics from song object
    try:
        lyrics = song.lyrics
    except Exception as err:
        log.error(f"Failed getting lyrics for song {song_title}: {err}")
        raise err
    return lyrics


def store_song_lyrics_to_dict(song: str, artist: str, lyrics: str) -> None:
    """Stores the song with its artist and lyrics in the dict.

    Args:
        song (str): the song
        artist (str): the artist of the song
        lyrics (str): the lyrics of the song
    """
    # create entry for artist if necessary
    if artist not in lyrics_dict:
        artist_dict = {}
        lyrics_dict[artist] = artist_dict

    # create entry for song and lyrics
    if song not in lyrics_dict[artist]:
        lyrics_dict[artist][song] = lyrics
        log.info(f"Stored song {song} of artist {artist} in dict")
    else:
        log.info(f"Skipping already existing song {song} of artist {artist}")


def lyrics_dict_to_json(file_name: str) -> None:
    """Saves the lyrics_dict as a .json file.

    Args:
        file_name (str): name of the json file
    """
    if file_name is None:
        log.error(f"Unspecified file name of lyrics.json")
        return

    # path to target json
    lyrics_json_path = os.getenv("DATA_PATH") + "\\lyrics_" + file_name + ".json"

    # write dict into file
    with open(lyrics_json_path, "a") as lyrics_json:
        json.dump(lyrics_dict, lyrics_json, indent=4)

        log.info(f"Stored lyrics_dict in file at {lyrics_json_path}")


def get_song_list(cnx: sqlite3.Connection, cursor: sqlite3.Cursor) -> List[List[str]]:
    """Query db and return for list of (song_id, song_name, song_artist) tuples.

    Args:
        cnx (sqlite3.Connection): the connection to the db
        cursor (sqlite3.Cursor): the cursor of the db

    Raises:
        Error: unknown error during sql query execution
    """

    query = """
        SELECT tracks.id, tracks.name, artists.name
        FROM tracks
        INNER JOIN artists ON tracks.primary_artist_id == artists.id
    """

    try:
        cursor.execute(query)
        cnx.commit()
        results = cursor.fetchall()
    except sqlite3.Error as err:
        log.error(f"Failed to query all songs in table tracks: {err}")
        cnx.rollback()
        raise err
    return results


def run_lyrics_getter(file_name: str) -> None:
    """Get lyrics for all tracks in spotfiy_ds and store them in .json file.

    Args:
        file_name (str): name of the .json file
    """

    # main entry
    connect_to_api()
    cnx, cursor = db.connect_to_db("test_db")  # temporary hardcoded db name

    # query db to get list of all (song_id, song_name, artist) tuples
    song_list = get_song_list(cnx, cursor)

    # get lyrics for each song
    for song in song_list:
        lyrics = get_song_lyrics(song[1], song[2])

        # check for language, type, (encoding?)
        if not lp.valid_lyrics(lyrics):
            # TODO delete from spotify_db?
            continue

        # clean lyrics
        lyrics = lp.clean_lyrics(lyrics)
        store_song_lyrics_to_dict(song[1], song[2], lyrics)

    # store in -> \data\datasets\lyrics\file_name.json
    lyrics_dict_to_json(file_name)
