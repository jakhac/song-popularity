import logging
import math
import sys

# from ..database import db_interface as db

# log = logging.getLogger("lyrics")


def score_lyrics():
    # word cnt

    lyrics = """Giving praise to mother nature Aten, Atun, Neteru
    Praise to my people who traveled here from Nibiru
    Praise to Nuwaubians the one they callin' the widows
    Praise the graves, raise us universal pharaohs'
    Giving praise to mother nature Aten, Atun, Neteru
    Praise to my people who traveled here from Nibiru
    Praise to Nuwaubians the one they callin' the widows
    Praise the graves, raise us universal pharaohs'
    Praise the graves, raise us universal pharaohs'
    Praise the graves, raise us universal pharaohs'
    """
    word_count = count_words(lyrics)
    # diversity

    # repetition
    rep_score = repetition(lyrics)
    print(rep_score)
    # more features?

    # insert into db
    pass


def repetition(lyrics: str) -> int:
    n = 5
    rep_score = 0
    lst = list(filter(None, lyrics.split(" ")))
    print(lst)
    for i in range(1, n + 1):
        rep_score += calc_tuple_reps(lst, i) * math.exp(-0.1 * i)
    rep_score /= n
    if rep_score > 1:
        # log.critical("Formula is not working. Score > 1.")
        exit(1)
    return rep_score


def calc_tuple_reps(lyrics_split: str, i: int):

    tpls = []
    for j in range(0, len(lyrics_split) - i + 1):
        tpls.append(" ".join(lyrics_split[j : i + j]))

    len_tpls = len(tpls)
    print(len_tpls)
    uniq_tpls = list(set(tpls))

    return (
        sum(filter(lambda n: n > 1, list(map(lambda x: tpls.count(x), uniq_tpls))))
        / len_tpls
    )


def count_words(lyrics: str) -> int:
    """Computes the number of words for a given lyrics.

    Args:
        lyrics (str): the given lyrics

    Raises:
        TypeError: lyrics not instance of str

    Returns:
        int: # words
    """
    try:
        count = len(lyrics.split(" "))
        return count
    except TypeError as err:
        # log.error(f"TypeError while computing word count: {err}")
        raise err


def word_diversity(lyrics: str) -> float:
    """Computes the amount of different words for a given lyrics.

    Args:
        lyrics (str): the given lyrics

    Raises:
        TypeError: lyrics not instance of str
        ZeroDivisionError: word count for lyrics is zero

    Returns:
        float: word diversity ratio: # different words/# words
    """
    try:
        diversity = len(set(lyrics.split(" "))) / count_words(lyrics)
        return diversity
    except TypeError as err:
        # log.error(f"TypeError while computing word diversity: {err}")
        raise err
    except ZeroDivisionError as zero:
        # log.error("ZeroDivisionError while computing word diversity: word count is 0.")
        raise zero


score_lyrics()
