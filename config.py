#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import os

from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv()

API_KEY = os.getenv("API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))
DB_PATH = os.path.join(basedir, "app", "db", "database.db")
REDEYE_URL = "https://www.redeyerecords.co.uk"
REDEYE_CDN = "https://redeye-391831.c.cdn77.org"
PARSER_JSON = os.path.join(basedir, "parser.json")
APP_HOST = "https://redeyerecordsbot.ru/"
API_HOST = APP_HOST + "api/v1"

api_key_headers = {"x-api-key": API_KEY}

headers = {
    "accept": "*/*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/73.0.3683.103 Safari/537.36"
}
genre_ids = [
    "bassSubmenu",
    "dabSubmenu",
    "expSubmenu",
    "fhsSubmenu",
    "hdSubmenu",
    "regSubmenu",
    "tecSubmenu",
    "balSubmenu",
    "altSubmenu"
]
genres = {
    "bass_music": "BASS MUSIC",
    "drum_bass_jungle": "DRUM & BASS / JUNGLE",
    "ambient_experimental_drone": "AMBIENT / EXPERIMENTAL / DRONE",
    "hip_hop_soul_jazz_funk": "HIP HOP / SOUL / JAZZ / FUNK",
    "house_disco": "HOUSE / DISCO",
    "reggae": "REGGAE",
    "techno_electro": "TECHNO / ELECTRO",
    "balearic_downtempo": "BALEARIC / DOWNTEMPO",
    "alternative_indie_folk_punk": "ALTERNATIVE / INDIE / FOLK / PUNK",
}
