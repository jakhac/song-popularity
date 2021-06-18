import logging
import logging.config
import sys

from .logging_config import LOGGING_CONFIG
from .lyrics_dataset.lyrics_api import connect_to_api, run_lyrics_getter

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

    if len(args) == 0:
        log.info("No command line arguments passed")
    else:
        log.info(f"Passed {len(args)} command line arguments ")

    if script == "connect_to_api":
        log.info("Calling script 'connect_to_api'")
        connect_to_api()
    elif script == "run_lyrics_getter":
        if len(args) != 0:
            log.info(f"Calling script 'run_lyrics_getter' with argument '{args[0]}'")
            run_lyrics_getter(str(args[0]))
        else:
            log.info("Calling script 'run_lyrics_getter'")
            run_lyrics_getter()
    else:
        log.critical(f"Unknown script '{script}', exiting program.")
        exit(1)


if __name__ == "__main__":
    main()
