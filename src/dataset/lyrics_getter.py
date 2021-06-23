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

from ..database import db_interface as db
from ..dataset.preprocessing import content_is_lyrics, valid_lyrics, clean_lyrics


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

    # This lyrics path does not exist, checked in run_lyrics_getter
    lyrics_path = os.getenv("DATA_PATH") + "\\datasets\\lyrics\\" + song_id + ".txt"

    # write lyrics into file
    with open(lyrics_path, "a", encoding="utf-8") as file:
        file.write(lyrics)

    log.info(f"Stored lyrics of song_id {song_id}")


def lyrics_stored(song_id: str) -> bool:
    """Check if a txt file named song_id is alread stored in lyrics folder.

    Args:
        song_id (str): song_id, used as name of the json file
    """
    lyrics_file_path = (
        os.getenv("DATA_PATH") + "\\datasets\\lyrics\\" + song_id + ".txt"
    )

    # skip if already stored
    return os.path.isfile(lyrics_file_path)


def get_song_list(cnx: sqlite3.Connection, cursor: sqlite3.Cursor) -> List[List[str]]:
    """Query db and return for list of (song_id, song_name, song_artist) tuples.

    Args:
        cnx (sqlite3.Connection): the connection to the db
        cursor (sqlite3.Cursor): the cursor of the db

    Raises:
        Error: unknown error during sql query execution
    """

    query = """
        SELECT tf.id, tf.name, artists.name
        FROM tracks_filtered AS tf
        INNER JOIN artists ON tf.primary_artist_id == artists.id;
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


def signal_handler(sig, frame):
    """Signal handler for CTRL + C. Store all current songs to json and exit script.

    Args:
        sig : signal
        frame : frame
    """
    signal.signal(sig, signal.SIG_IGN)
    log.critical("Abort run_lyrics_getter script.")
    # lyrics_dict_to_json("abort_" + "{:%Y-%m-%d_%H-%M-%S}".format(datetime.now()))
    sys.exit(0)


def run_lyrics_getter() -> None:
    """Get lyrics for all tracks in spotfiy_ds and store them in .json file."""

    # Set handler functinon for ctrl+c signal
    signal.signal(signal.SIGINT, signal_handler)

    connect_to_api()
    cnx, cursor = db.connect_to_db("spotify_ds_filtered")  # temporary hardcoded db name

    # query db to get list of all (song_id, song_name, artist) tuples
    song_list = get_song_list(cnx, cursor)
    len_songs = len(song_list)

    for i in range(0, len(song_list)):

        if i % 100 == 0:
            print(f"Processed: {i}/{len_songs}")

        # Skip, if lyrics are already stored
        if lyrics_stored(song_list[i][0]):
            log.info(f"Skip lyrics for song_id {song_list[i][0]}, already stored.")
            continue

        try:
            lyrics = get_song_lyrics(song_list[i][1], song_list[i][2])
        except Exception:
            log.warning(f"Skipping song {song_list[i]}, no lyrics found.")
            continue

        if not valid_lyrics(lyrics):
            log.info(f"Skipping song {song_list[i][1]}: invalid lyrics")
            continue

        lyrics = clean_lyrics(lyrics)
        store_lyrics_to_txt(song_list[i][0], lyrics)
        # store_song_lyrics_in_dict(song[0], lyrics)

    print("Finished getting all songs.")
    # store in -> \data\datasets\lyrics\file_name.json
    # lyrics_dict_to_json(file_name)
