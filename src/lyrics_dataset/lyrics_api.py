import lyricsgenius as api
import os
import logging
import logging.config

from dotenv import load_dotenv

load_dotenv()


log = logging.getLogger("lyrics")

genius = None
lyrics_dict = {}

def connect_to_api() -> None:
    """Access Genius API via access token and declare instance of Genius class.
    """    
    global genius
    log.info("Connecting to Genius API...")
    try: 
        genius = api.Genius(os.getenv("GENIUS_ACCESS_TOKEN"))
    except Exception as err:
        log.critical(f"Error while connecting to Genius API: {err}")
        log.info("Exiting...")
        exit(1)
    log.info("Connected to Genius API.")


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
    # get song object fron genius
    try:
        song = genius.search_song(song_title, artist)
    except Exception as err:
        log.error(f"Error while getting object for song {song_title}: {err}")
        raise err
    
    # get lyrics from song object
    try:
        lyrics = song.lyrics
        return lyrics
    except Exception as err:
        log.error(f"Error while getting lyrics for song {song_title}: {err}")
        raise err
    

def save_lyrics(lyrics: str, song: str, artist: str) -> None:
    pass


def run_lyrics_getter():
    # main entry
    # connect_to_api()
    pass

# artist = genius.search_artist("Andy Shauf", max_songs=3, sort="title")
# print(artist.songs)
# print(artist.song("Alexander All Alone").lyrics)
