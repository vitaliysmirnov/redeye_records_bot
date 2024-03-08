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
APP_HOST = "https://redeyerecordsbot.ru/"
API_HOST = APP_HOST + "api/v1"

REDEYE_IDS_LIMIT = 1000
PARSER_COOL_DOWN = 300

api_key_headers = {"x-api-key": API_KEY}

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
