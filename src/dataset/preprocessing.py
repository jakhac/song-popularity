import logging
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
    track_row[6] = track_row[6][0]

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

    # remove genres from row
    genres = []
    genres.extend(artist_row.pop(2))

    return (artist_row, genres)
