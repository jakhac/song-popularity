import re
import logging
from langdetect import detect

from typing import List, Optional, Tuple

log = logging.getLogger("preprocessing")


def process_track_row(track_row: List[str]) -> Optional[List[str]]:
    """Processes a row from tracks.csv for inserting it as a track into the db.

    Args:
        track_row (List[str]): the track row to be processed

    Returns:
         Optional[List[str]]: the processed track row
    """
    if not track_row or len(track_row) != 20:
        log.warn(
            f"Invalid track row format: row is NoneType, empty or has not 20 values"
        )
        return

    # set primary_artist_id to first from artists_id list
    track_row[6] = track_row[6][1:-1].split(",")[0].replace("'", "")

    # extract release year from date with format (YYYY-MM-DD) to (YYYY)
    track_row[7] = track_row[7][:4]

    # remove artists list
    track_row.pop(5)
    return track_row


def process_artist_row(artist_row: List[str]) -> Optional[Tuple[List[str], List[str]]]:
    """Processes a row from artists.csv for inserting it as an artist into the db and extracts the genres of the artist.

    Args:
        artist_row (List[str]): the artist row to be processed
    Returns:
         Optional[Tuple[List[str], List[str]]]: (processed artist row, genres)
    """

    if not artist_row or len(artist_row) != 5:
        log.warn(f"Invalid artist row: row is NoneType, empty or has not 5 values")
        return

    # Convert string into list of strings
    genres = (artist_row[2])[1:-1].split(",")
    genres = [g.replace("'", "").replace('"', "").strip() for g in genres]
    genres = list(filter(None, genres))

    # remove genres from row
    artist_row.pop(2)

    return (artist_row, genres)


def valid_lyrics(lyrics: str) -> str:
    """Check if lyrics are valid. Valid lyrics are from type str and english.

    Args:
        lyrics (str): the lyrics of the song

    Returns:
        (bool): True if lyrics are valid, else False
    """
    # type string?
    if not isinstance(lyrics, str):
        return False

    # lang english?
    if detect(lyrics) != "en":
        return False

    return True


def clean_lyrics(lyrics: str) -> str:
    """Remove special tokens from lyrics

    Args:
        lyrics (str): the lyrics of the song

    Returns:
        (str): cleaned lyrics
    """

    # Remove special tokens
    pattern = re.compile("/\[(\w|\s)*\]/g")
    return re.sub(pattern, str.replace, str(lyrics))
