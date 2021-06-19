import json
import logging
import logging.config
import os

import lyricsgenius as api

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
        return lyrics
    except Exception as err:
        log.error(f"Failed getting lyrics for song {song_title}: {err}")
        raise err


def store_song_lyrics(song: str, artist: str, lyrics: str) -> None:
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


def run_lyrics_getter(file_name: str) -> None:
    """Get lyrics for tracks from spotfiy_ds and store them in .json file.

    Args:
        file_name (str): name of the .json file
    """
    raise NotImplementedError
    # main entry
    # connect_to_api()

    # get (song, primary_artist) list from spotify ds

    # for loop
    # get lyrics for each song

    # song_name = "Never Say Never"
    # song_artist = "Jaden"
    # lyrics = get_song_lyrics(song_name, song_artist)

    # store_song_lyrics(song_name, song_artist, lyrics)

    # lyrics_dict_to_json(file_name)
    # -> \data\datasets\lyrics\file_name.json
