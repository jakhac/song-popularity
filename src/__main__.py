import logging
import logging.config
import os
import sys

from dotenv import load_dotenv

from .database.db_backup import dump_db, load_db_dump
from .database.db_setup import create_db
from .dataset.lyrics_getter import connect_to_api, run_lyrics_getter
from .dataset.preprocessing import filter_tracks
from .dataset.spotify_ds_reader import read_artists_csv, read_tracks_csv
from .logging_config import LOGGING_CONFIG
from .training.music_features import train

load_dotenv()

logging.config.dictConfig(LOGGING_CONFIG)


def main():
    logging.config.dictConfig(LOGGING_CONFIG)
    log = logging.getLogger("main")
    log.info("Starting programm")

    # check if script has been specified
    if len(sys.argv) == 1:
        log.critical("No script specified, exiting program.")
        exit(1)

    # get script name
    script = sys.argv[1]

    # get script arguments
    args = sys.argv[2:]

    # check if DATA_PATH env has been defined
    if os.getenv("DATA_PATH") is None:
        log.critical(
            "Undefined DATA_PATH environmental variable. Define DATA_PATH in .env file."
        )
        exit(1)

    if len(args) == 0:
        log.info("No command line arguments passed")
    else:
        log.info(f"Passed {len(args)} command line arguments ")

    if script == "connect_to_api":
        log.info("Calling script 'connect_to_api'")
        connect_to_api()
    elif script == "run_lyrics_getter":
        log.info("Calling script 'run_lyrics_getter'")
        run_lyrics_getter()
    elif script == "read_artists_csv":
        log.info(f"Calling script 'read_artists_csv' with argument '{args[0]}'")
        read_artists_csv(str(args[0]))
    elif script == "read_tracks_csv":
        log.info(f"Calling script 'read_tracks_csv' with argument '{args[0]}'")
        read_tracks_csv(str(args[0]))
    elif script == "dump_db":
        if len(args) != 0:
            log.info(f"Calling script 'dump_db' with argument '{args[0]}'")
            dump_db(str(args[0]))
        else:
            log.critical("No arguments specified for script 'dump_db'")
    elif script == "load_db":
        if len(args) != 0:
            log.info(f"Calling script 'load_db' with argument '{args[0]}'")
            load_db_dump(str(args[0]))
        else:
            log.critical("No arguments specified for script 'load_db'")
    elif script == "create_db":
        if len(args) != 0:
            log.info(f"Calling script 'create_db' with argument '{args[0]}'")
            create_db(str(args[0]))
        else:
            log.critical("No arguments specified for script 'create_db'")
    elif script == "filter_tracks":
        log.info(f"Calling script 'filter_tracks'")
        filter_tracks()
    elif script == "train":
        log.info(f"Calling script 'train'")
        train()
    else:
        log.critical(f"Unknown script '{script}', exiting program.")
        exit(1)


if __name__ == "__main__":
    main()
