#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import sqlite3
from os import path

from config import DB_PATH


def main():
    if not path.isfile(DB_PATH):
        db_connection = sqlite3.connect(DB_PATH)
        db_cursor = db_connection.cursor()
        db_cursor.execute(create_users)
        db_cursor.execute(create_subscriptions)
        db_connection.commit()
        db_connection.close()
        print("Database created")
    else:
        print("Database already exists")


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

create_subscriptions = """
    CREATE TABLE subscriptions (
        user_id INT PRIMARY KEY,
        bass_music BOOLEAN,
        drum_and_bass BOOLEAN,
        experimental BOOLEAN,
        funk_hip_hop_soul BOOLEAN,
        house_disco BOOLEAN,
        reggae BOOLEAN,
        techno_electro BOOLEAN,
        balearic_and_downtempo BOOLEAN,
        alternative_indie_folk_punk BOOLEAN
);
"""


if __name__ == "__main__":
    main()
