import csv
import logging
import os

from ..database import db_interface as db

log = logging.getLogger("dataset")


def read_tracks_csv(db_name: str):
    """Reads tracks.csv and inserts into spotify_ds db."""

    # connect to db
    cnx, cursor = db.connect_to_db(db_name)

    skipped_tracks = []

    tracks_csv_path = os.getenv("DATA_PATH") + "\\datasets\\spotify\\tracks.csv"
    with open(tracks_csv_path, encoding="utf-8") as tracks_csv:
        # read raw label data
        tracks_reader = csv.reader(tracks_csv)
        log.info(f"Reading tracks.csv from path {tracks_csv_path}")

        # skip first row to remove column names
        next(tracks_reader, None)

        for row in tracks_reader:
            try:
                db.insert_track(row, cnx, cursor)
            except Exception as err:
                log.warning(f"Skipping track with id {row[0]} due to error: {err}")
                skipped_tracks.append(row)
                continue

    if len(skipped_tracks) > 0:
        log.warn(f"Skipped {len(skipped_tracks)} tracks")

    log.info("Completed reading tracks.csv")


def read_artists_csv(db_name: str):
    """Reads artists.csv and inserts into spotify_ds db."""

    # connect to db
    cnx, cursor = db.connect_to_db(db_name)

    skipped_artists = []

    artists_csv_path = os.getenv("DATA_PATH") + "\\datasets\\spotify\\artists.csv"
    with open(artists_csv_path, encoding="utf-8") as artists_csv:
        # read raw label data
        artists_reader = csv.reader(artists_csv)
        log.info(f"Reading artists.csv from path {artists_csv_path}")

        # skip first row to remove column names
        next(artists_reader, None)

        for row in artists_reader:
            try:
                db.insert_artist(row, cnx, cursor)
            except Exception as err:
                log.warning(f"Skipping artist with id {row[0]} due to error: {err}")
                skipped_artists.append(row)
                continue

    if len(skipped_artists) > 0:
        log.warn(f"Skipped {len(skipped_artists)} artists")

    log.info("Completed reading artists.csv")
