import logging
import re
import logging
from langdetect import detect

from ..database import db_interface as db

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
        AND tracks.primary_artist_id == (?)
        ORDER BY LENGTH(tracks.name) ASC;
    """

    cursor.execute(artists_query)
    artist_id_list = cursor.fetchall()
    len_artists = len(artist_id_list)
    print("Length artists ", len_artists)

    # For every artist that has released after 2000...
    for i in range(0, len_artists):
        # ... get song list with artist id
        cursor.execute(song_query, artist_id_list[i])
        song_name_list = cursor.fetchall()

        # Filter similar songs, keep highest popularity
        distinct_songs = filter_similar_song_names(song_name_list)

        # [print(s[:3]) for s in song_name_list]
        # print("Filtered list")
        # [print(d[:3]) for d in distinct_songs]
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
    best_indices = []
    skip_indices = []

    # For every track ...
    for i in range(0, len(track_rows)):

        # skip songs which are already considered due to similarity to a previous song
        if i in skip_indices:
            continue

        # Current song is supposed to be the best
        best_idx = i
        best_pop = track_rows[i][2]

        # For all songs ...
        j = i + 1
        while j < len(track_rows) and j not in skip_indices:

            # ... and similar song name
            if track_rows[i][1] in track_rows[j][1]:
                # Always invalidate, as this song is considered now
                skip_indices.append(j)

                # Look for highest popularity among similar songs
                if best_pop < track_rows[j][2]:
                    best_pop = track_rows[j][2]
                    best_idx = j

            j += 1

        # Append index with best popularity
        best_indices.append(best_idx)

    # Add entries of best indices
    return [track_rows[i] for i in best_indices]


def valid_lyrics(lyrics: str) -> str:
    """Check if lyrics are valid. Valid lyrics are from type str and english.

    Args:
        lyrics (str): the lyrics of the song

    Returns:
        (bool): True if lyrics are valid, else False
    """
    # type string?
    if lyrics is None or not isinstance(lyrics, str):
        return False

    # lang english?
    lang = ""
    try:
        lang = detect(lyrics)
    except Exception as err:
        log.error(f'Failed to detect language of "{lyrics[:10]}" due to error {err}')
        return False

    if lang != "en":
        return False

    # string is lyrics (not list of artists, novel, ..)
    if not content_is_lyrics(lyrics):
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


def content_is_lyrics(input_content: str):
    """Checks if the input content is lyrics and not some kind of enumeration.

    Args:
        input_lyrics (str): the content to be checked

    Returns:
        bool: True, if the content is lyrics, otherwise False
    """

    # Roughly above 10KB
    if len(input_content) >= 6400:
        return False

    invalid_lines = 0
    valid_lines = 0

    lines = input_content.splitlines()
    for line in lines:
        if not len(line):
            continue

        if "-" in line or "--" in line or "–" in line:
            invalid_lines += 1
        elif "Psalms" in line:
            return False
        else:
            # if lines does not contain '-' or similar
            valid_lines += 1

        # checked at most 19 lines in each file
        if invalid_lines >= 10:
            return False
        elif valid_lines >= 10:
            return True

    return True
