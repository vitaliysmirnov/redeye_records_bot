#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import os
import logging

import sqlite3
from os import path

from config import DB_PATH, genres, basedir


def main():
    if not path.isfile(DB_PATH):
        db_connection = sqlite3.connect(DB_PATH)
        db_cursor = db_connection.cursor()
        db_cursor.execute(create_users)
        db_cursor.execute(create_subscriptions)
        db_connection.commit()
        db_connection.close()
        logging.info("Database created")
    else:
        logging.info("Database already exists")


create_users = """
    CREATE TABLE users (
        user_id INT PRIMARY KEY,
        user_chat_id BIGINT,
        username VARCHAR,
        first_name VARCHAR,
        last_name VARCHAR,
        is_active BOOLEAN,
        registered_at TIMESTAMP
);
"""

create_subscriptions = f"CREATE TABLE subscriptions (user_id INT PRIMARY KEY, {', '.join([genre + ' BOOLEAN' for genre in genres])});"


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        # filename=os.path.join(basedir, "database_setup.log"),
        # filemode="a",
        format="[%(filename)s] %(asctime)s %(levelname)s %(message)s"
    )

    main()
