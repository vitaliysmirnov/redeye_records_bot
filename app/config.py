#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

from os import environ

import psycopg2
import psycopg2.extras


REDEYE_URL = "https://www.redeyerecords.co.uk"
REDEYE_CDN = "https://redeye-391831.c.cdn77.org"
DB_TOKEN = "postgres://bhrywlqe:qKlZv9LjFbZx-TOH559ZKPRkhd4RVc6V@surus.db.elephantsql.com/bhrywlqe"
BOT_TOKEN = "7089771057:AAGY-y_RswUB9b_640y7QoFl8IbXffonBBo"
ADMIN_CHAT_ID = 230217326
APP_HOST = "http://localhost:5000/"
API_HOST = APP_HOST + "api/v1"

HOST = "0.0.0.0"
PORT = int(environ.get("PORT", 5000))

selections = {
    "bass_music": "BASS MUSIC",
    "drum_and_bass": "DRUM & BASS • JUNGLE",
    "experimental": "AMBIENT • EXPERIMENTAL • DRONE",
    "funk_hip_hop_soul": "HIP HOP • SOUL • JAZZ • FUNK",
    "house_disco": "HOUSE • DISCO",
    "reggae": "REGGAE",
    "techno_electro": "TECHNO • ELECTRO",
    "balearic_and_downtempo": "BALEARIC • DOWNTEMPO",
    "alternative_indie_folk_punk": "ALTERNATIVE / INDIE / FOLK / PUNK",
}
tables = {
    "preorders": "PRE-ORDER",
    "new": "NEW RELEASE",
    "discount30": "30% SALE",
    "discount50": "50% SALE",
    "discount75": "75% SALE",
}

"""
    CREATE TABLE users (
        user_id SERIAL PRIMARY KEY,
        chat_id VARCHAR,
        username VARCHAR,
        first_name VARCHAR,
        last_name VARCHAR,
        is_active BOOLEAN,
        registered_at TIMESTAMP
    );
"""
"""
    CREATE TABLE config (
        admin_chat_id VARCHAR,
        telegram_api_token VARCHAR
);
"""
