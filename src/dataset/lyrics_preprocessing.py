from langdetect import detect

special_tokens = [
    "[Intro]"
    "[Verse 1]"
    "[Verse 2]"
    "[Verse 3]"
    "[Verse 4]"
    "[Chorus]",
    "[Refrain]",
    "[Outro]"
]

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
    print(detect(lyrics))
    if detect(lyrics) != "en":
        return False

    return True


def clean_lyrics(lyrics: str) -> str:
    """Remove special tokens from lyrics and force ascii-characters only.

    Args:
        lyrics (str): the lyrics of the song

    Returns:
        (str): clean lyrics
    """
    # Remove non-ascii characters
    lyrics = lyrics.encode("ascii", "ignore")

    # Remove special characters
    for s in special_tokens:
        lyrics.replace(s, "")

