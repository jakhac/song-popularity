import logging
import logging.config
from .logging_config import LOGGING_CONFIG
import sys

from .lyrics_dataset.lyrics_api import connect_to_api

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

    if script == "connect_to_api":
        log.info("Calling script 'connect_to_api'")
        connect_to_api()
    else:
        log.critical(f"Unknown script '{script}', exiting program.")
        exit(1)



if __name__ == "__main__":
    main()
