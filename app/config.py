#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

from os import environ, path

import secrets


ADMIN_CHAT_ID = secrets.ADMIN_CHAT_ID
BOT_TOKEN = secrets.BOT_TOKEN
DB_PATH = f"{path.abspath(__name__).split('redeye_records_bot_v2')[0]}redeye_records_bot_v2/app/db/database.db"
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
