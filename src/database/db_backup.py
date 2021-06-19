import logging
import os
import sqlite3
from datetime import datetime
from posixpath import split
from sqlite3.dbapi2 import connect

from .db_interface import connect_to_db


def dump_db(db_name: str):
    """Dumps the specified database into a .sql file.

    Args:
        db_name (str): the name of the database
    """
    dump_path = (
        os.getenv("DATA_PATH")
        + "\\databases\\dumps\\"
        + db_name
        + ";"
        + "{:%Y-%m-%d_%H-%M-%S}".format(datetime.now())
        + ".sql"
    )

    if not os.path.exists(os.path.dirname(dump_path)):
        # create dirs on path if not exist
        os.makedirs(os.path.dirname(dump_path))

    cnx, cursor = connect_to_db(db_name)

    with open(dump_path, "w", encoding="utf-8") as dump_file:
        for line in cnx.iterdump():
            dump_file.write("%s\n" % line)

    cnx.close()


def load_db_dump(db_name: str):
    """Loads the most recent database dump for the specifed database.

    Args:
        db_name (str): the name of the database
    """
    # get all files in dir
    dumps_dir = os.getenv("DATA_PATH") + "\\databases\\dumps\\"
    dumps_list = os.listdir(dumps_dir)

    # filter files of the db with db_name
    dumps_list = list(
        filter(lambda file_name: file_name.split(";")[0] == db_name, dumps_list)
    )

    # sort list of files on dates
    dumps_list.sort(
        key=lambda file: datetime.strptime(file, f"{db_name};%Y-%m-%d_%H-%M-%S.sql")
    )

    # get latest dump from sorted file list
    latest_dump_file = dumps_dir + dumps_list[-1]

    # read dump
    f = open(latest_dump_file, "r", encoding="utf-8")
    sql_dump = f.read()

    db_path = os.getenv("DATA_PATH") + "\\databases\\binaries\\" + db_name + ".db"

    # create database
    cnx = connect(db_path)

    # load dump into database
    cnx.cursor().executescript(sql_dump)
    cnx.close()
