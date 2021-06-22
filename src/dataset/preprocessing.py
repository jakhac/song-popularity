import logging
import re
from typing import List, Optional, Tuple

from langdetect import detect

from ..database import db_interface as db

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


def filter_tracks():
    """Filter tracks from db.tracks table and store them in tracks_filtered table."""
    cnx, cursor = db.connect_to_db("spotify_ds_filtered")

    # Get list of artists with modern songs
    artists_query = """
        SELECT DISTINCT artists.id
        FROM artists 
        INNER JOIN tracks ON artists.id == tracks.primary_artist_id
        WHERE tracks.release_year >= 2000;
    """

    song_query = """
        SELECT *
        FROM tracks
        WHERE tracks.release_year >= 2000
        AND tracks.primary_artist_id == ?
        ORDER BY LENGTH(tracks.popularity) DESC;
    """

    cursor.execute(artists_query)
    artist_id_list = cursor.fetchall()
    len_artists = len(artist_id_list)

    # For every artist that has released after 2000...
    for i in range(0, len_artists):
        # ... get song list with artist id
        cursor.execute(song_query, artist_id_list[i])
        song_name_list = cursor.fetchall()

        # Filter similar songs, keep highest popularity
        distinct_songs = filter_similar_song_names(song_name_list)

        # [print(s) for s in song_name_list]
        # print("Filtered list")
        # [print(d) for d in distinct_songs]
        # print()
        # print()

        # Add most popular distinct songs into new table
        for d in distinct_songs:
            try:
                db.insert_filtered_track(d, cnx, cursor)
            except Exception as err:
                log.warning(f"Skipping track with id {d[0]} due to error: {err}")

        # Info every 100 artists
        if i % 100 == 0.0:
            print(f"Processed artists: {i}/{len(artist_id_list)}")
            log.info(f"Processed artists: {i}/{len(artist_id_list)}")

    log.info("Finished processing artists.")


def filter_similar_song_names(track_rows: List[List[str]]) -> List[List[str]]:
    """Filter a list of track_rows. Group similar starting song names and
    choose the one with highest popularity among them.

    Args:
        track_row (List[List[str]]): the track_rows to be filtered

    Returns:
        List[List[str]]: the filtered list of track_rows
    """
    # Contains the tuples of distinct song_names with maximal popularity
    distinct_rows = []

    # Flag is set to true, if in cur_row "%name%" is already distinct rows
    found_match = False

    # Longest strings are considered first.
    for cur_row in track_rows:

        # Try to insert current row into list of distinct rows
        # All long strings (e.g. containing .feat) are inserted first
        for i in range(0, len(distinct_rows)):
            found_match = False

            # If current row is already in distinct_rows, replace entry if popularity can be
            # improved. Later entries can still improve replacements, because strings ordered
            # decreasing in length.
            if cur_row[1] in distinct_rows[i][1]:
                found_match = True

                # Popularity of similar song can be improved
                if cur_row[2] > distinct_rows[i][2]:
                    distinct_rows[i] = cur_row

                break

        # Name of cur_row does not exist in distinct_rows yet
        if not found_match:
            distinct_rows.append(cur_row)

    return distinct_rows


def content_is_lyrics(input_content: str):
    """Checks if the input content is lyrics and not some kind of enumeration.

    Args:
        input_lyrics (str): the content to be checked

    Returns:
        bool: True, if the content is lyrics, otherwise False
    """
    if input_content is None or not isinstance(input_content, str):
        return False

    lines = input_content.splitlines()

    if lines >= 300:
        return False

    invalid_lines = 0
    valid_lines = 0

    for line in lines:
        if "-" in line:
            invalid_lines += 1
        elif "Psalms" in line:
            return False
        else:
            # if lines does not contain '-'
            valid_lines += 1

        # checked at most 19 lines in each file
        if invalid_lines >= 10:
            return False
        elif valid_lines >= 10:
            return True

    return True
