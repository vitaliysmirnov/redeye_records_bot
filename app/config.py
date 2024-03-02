#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

from os import environ

import secrets


ADMIN_CHAT_ID = secrets.ADMIN_CHAT_ID
BOT_TOKEN = secrets.BOT_TOKEN
DATABASE_URL = secrets.DATABASE_URL
REDEYE_URL = "https://www.redeyerecords.co.uk"
REDEYE_CDN = "https://redeye-391831.c.cdn77.org"
APP_HOST = "http://localhost:8444/"
API_HOST = APP_HOST + "api/v1"

HOST = "0.0.0.0"
PORT = int(environ.get("PORT", 8444))

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
        user_chat_id BIGINT,
        username VARCHAR,
        first_name VARCHAR,
        last_name VARCHAR,
        is_active BOOLEAN,
        registered_at TIMESTAMP
);
"""
"""
    CREATE TABLE subscriptions (
        user_id INT,
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
