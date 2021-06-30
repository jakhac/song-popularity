import logging
import math
import statistics
import sys

from typing import List

from ..database import db_interface as db
from .lyrics_getter import get_unscored_songs, get_lyrics_from_file

log = logging.getLogger("lyrics")


def run_lyrics_scorer():
    log.info("Running lyrics scorer...")
    cnx, cursor = db.connect_to_db("spotify_ds")
    song_list = get_unscored_songs(cnx, cursor)  # (song_id, song_name, artist_name)
    print(song_list)
    return
    log.info(f"Attempting to get lyrics for {len(song_list)} songs")
    skipped_songs = []
    processed_songs = 0

    for song in song_list:
        processed_songs += 1
        if processed_songs % 100 == 0:
            print(f"Song: {processed_songs}/{len(song_list)}")

        try:
            lyrics = get_lyrics_from_file(song[0])
        except Exception as err:
            log.error(f"Failed getting lyrics file for song {song[0]}: {err}")
            log.info(f"Skipping lyrics for song {song[0]}")
            skipped_songs.append(song[0])
            continue

        try:
            lyric_scores = score_lyrics(lyrics)
        except Exception as err:
            log.error(f"Failed inserting lyrics scores for song {song[0]}: {err}")
            skipped_songs.append(song[0])
            continue

        if lyric_scores is None:
            log.info(f"Skipping empty lyrics for song {song[0]}")
            skipped_songs.append(song[0])
            continue

        try:
            db.insert_lyric_scores(song[0], lyric_scores, cnx, cursor)
        except Exception as err:
            log.error(f"Failed inserting lyrics scores for song {song[0]}: {err}")
            skipped_songs.append(song[0])
            continue

    log.info(
        f"Skipped {len(skipped_songs)} out of {len(song_list)} songs: {skipped_songs}"
    )
    log.info("Lyrics scorer completed")


def score_lyrics(lyrics: str) -> List[float]:
    """Computes the scores for a given lyrics.

    Args:
        lyrics (List[str]): the given lyrics

    Returns:
        List[float]: (word_count, rep_score, div_score)
    """
    if not isinstance(lyrics, str):
        log.error("Lyrics not of type string, skipping")
        return

    lyrics = (
        lyrics.replace(",", " ")
        .replace("(", " ")
        .replace(")", " ")
        .replace("\n", " ")
        .lower()
    )

    lyrics_split = list(filter(None, lyrics.split(" ")))

    if not lyrics_split:
        log.warning("Empty list, skipping lyrics")
        return

    word_count = len(lyrics_split)
    print("word_count()=", word_count)

    rep_score = repetition_score(lyrics_split)
    print("repetition_score()=", rep_score)

    div_score = diversity_score(lyrics_split)
    print("diversity_score()=", div_score)

    return [word_count, rep_score, div_score]


def repetition_score(lyrics_split: List[str]) -> float:
    """Computes the reptition score for a given lyrics.

    Args:
        lyrics (List[str]): the given lyrics

    Returns:
        float: repetition score in [0,1]
    """
    return sum(
        [n for n in [lyrics_split.count(x) for x in set(lyrics_split)] if n > 1]
    ) / len(lyrics_split)


def diversity_score(lyrics_split: List[str]) -> float:
    """Computes the amount of different words for a given lyrics.

    Args:
        lyrics (List[str]): the given lyrics

    Returns:
        float: word diversity ratio: # different words/# words
    """
    return len(set(lyrics_split)) / len(lyrics_split)


# score_lyrics()
bts = """Euphoria
Take my hands now
You are the cause of my euphoria
Oh yeah, yeah, yeah, yeah, yeah, yeah (Oh)
Oh yeah, yeah, yeah, yeah, yeah, yeah (Euphoria)
Oh yeah, yeah, yeah, yeah, yeah, yeah
Close the door now
When I'm with you, I'm in utopia
"""
