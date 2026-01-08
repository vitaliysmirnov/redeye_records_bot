#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import re
import json
import sqlite3
import logging
from time import sleep
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

from config import API_HOST, DB_PATH, REDEYE_URL, REDEYE_CDN, PARSER_JSON, api_key_headers, genre_ids, headers


class Parser:
    """Parser is independent app module. Can be hosted anywhere"""
    def __init__(self, init=False):
        if init:
            session = requests.Session()
            request = session.get(REDEYE_URL, headers=headers)
            soup = BeautifulSoup(request.content, "html.parser")
            parser_json = dict()
            for g in genre_ids:
                genre = soup.find("a", attrs={"href": f"#{g}"}).text
                parser_json[genre] = {}
                genre_li = soup.find("ul", attrs={"id": g})
                for li in genre_li.findAll("li"):
                    section = li.find("a").text
                    if "chart" not in li.find("a")["href"].lower() and "Pre-Order Releases" not in section:
                        parser_json[genre][section] = {
                            "url": li.find("a")["href"],
                            "table": re.sub(r"\s*[/&|%-]+\s*|\s+", "_", f"{genre} {section}").lower()
                        }

            with open(PARSER_JSON, "w") as f:
                json.dump(parser_json, f, indent=4)

            self.parser_json = parser_json
        else:
            try:
                with open(PARSER_JSON) as json_file:
                    self.parser_json = json.load(json_file)
            except Exception as e:
                logging.warning(e)
                raise e

    def get_releases_from_url(self, url):
        """Get data from redeyerecords"""
        session = requests.Session()
        logging.info(f"Trying to get {url}")
        request = session.get(f"{url}", headers=headers)
        if request.status_code == 200:
            logging.debug(f"{url} status code: {request.status_code}")
            soup = BeautifulSoup(request.content, "html.parser")
            releases = soup.findAll("div", attrs={"class": "releaseGrid"})
            logging.info(f"{len(releases)} releases found at {url}")
            return releases
        else:
            logging.warning(f"{url} status code: {request.status_code}. Try again in 300 seconds.")
            sleep(300)
            self.get_releases_from_url(url)

    def set_db_tables(self):
        """Create tables in database"""
        db_connection = sqlite3.connect(DB_PATH)
        db_cursor = db_connection.cursor()

        for genre in self.parser_json:
            for section in self.parser_json[genre]:
                table = self.parser_json[genre][section]["table"]
                db_cursor.execute(
                    f"""
                        DROP TABLE IF EXISTS {table}
                    """
                )
                logging.info(f"Table {table} deleted")
                db_connection.commit()
                db_cursor.execute(
                    f"""
                        CREATE TABLE {table} (
                            item_id INT,
                            redeye_id INT,
                            title VARCHAR,
                            cat VARCHAR,
                            tracklist VARCHAR,
                            price VARCHAR,
                            release_url VARCHAR,
                            samples VARCHAR,
                            img VARCHAR,
                            genre VARCHAR,
                            section VARCHAR,
                            registered_at TIMESTAMP
                    );
                    """
                )
                db_connection.commit()
                logging.info(f"New table {table} created")

        db_connection.close()

    @staticmethod
    def parse_release_data(release):
        """Combine releases data from web for usage"""
        redeye_id = int(release["id"])
        title = release.find("p", attrs={"class": "artist"}).text
        cat = release.find("p", attrs={"class": "label"})
        cat = f"{cat.contents[2].text} – {cat.contents[0]}"
        tracklist = release.find("p", attrs={"class": "tracks"}).text
        samples = release.findAll("a", attrs={"class": "btn-play"})
        samples_str = ""
        if len(samples) > 0:
            samples_str = f"{REDEYE_CDN}/{redeye_id}.mp3"
            samples_str += "".join(
                [f",{REDEYE_CDN}/{redeye_id}{chr(i + 97)}.mp3" for i in range(1, len(samples))])
        samples = samples_str
        price = release.find("div", attrs={"class": "price"}).text.replace("\n", "").replace("!", "!\n")
        status = release.find("div", attrs={"class": "type"}).text
        img = release.find("img")["src"]
        release_url = release.find("a")["href"]

        return redeye_id, title, cat, tracklist, price, release_url, samples, img, status

    def db_initiation(self):
        """Method that fills database with actual releases data"""
        self.set_db_tables()

        db_connection = sqlite3.connect(DB_PATH)
        db_cursor = db_connection.cursor()

        for genre in self.parser_json:
            for section in self.parser_json[genre]:
                table, url = self.parser_json[genre][section]["table"], self.parser_json[genre][section]["url"]
                releases = self.get_releases_from_url(url)
                releases.extend(self.get_releases_from_url(f"{url}/page-2")) if len(releases) == 50 else None
                logging.info(f"Total of {len(releases)} releases parsed for {url}")
                for release in releases:
                    redeye_id, title, cat, tracklist, price, release_url, samples, img, status = self.parse_release_data(release)
                    db_cursor.execute(
                        f"""
                            INSERT INTO {table} 
                                (item_id, redeye_id, title, cat, tracklist, price, release_url, samples, img, genre, section, registered_at)
                            VALUES 
                                ((SELECT count(item_id) FROM {table}) + 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ;
                        """, (redeye_id, title, cat, tracklist, price, release_url, samples, img, genre, section, str(datetime.now(timezone.utc)))
                    )
                    db_connection.commit()

        db_connection.close()

    def check_new_releases(self):
        """Method that checks redeyerecords for new releases"""
        logging.info(f"========== Session started at {datetime.now(timezone.utc)} ==========")
        db_connection = sqlite3.connect(DB_PATH)
        db_cursor = db_connection.cursor()

        for genre in self.parser_json:
            for section in self.parser_json[genre]:
                table, url = self.parser_json[genre][section]["table"], self.parser_json[genre][section]["url"]
                db_cursor.execute(f"SELECT redeye_id FROM {table}")
                db_redeye_ids = db_cursor.fetchall()
                logging.debug(f"Redeye IDs in {table}: {db_redeye_ids}")
                releases = self.get_releases_from_url(url)
                for release in releases:
                    redeye_id, title, cat, tracklist, price, release_url, samples, img, status = self.parse_release_data(release)
                    if (redeye_id,) not in db_redeye_ids:
                        db_cursor.execute(
                            f"""
                                INSERT INTO {table} 
                                    (item_id, redeye_id, title, cat, tracklist, price, release_url, samples, img, genre, section, registered_at)
                                VALUES 
                                    ((CASE WHEN (SELECT count(item_id) FROM {table}) == 0 THEN 1 ELSE (SELECT max(item_id) FROM {table}) + 1 END), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ;
                            """, (redeye_id, title, cat, tracklist, price, release_url, samples, img, genre, section, str(datetime.now(timezone.utc)))
                        )
                        db_connection.commit()
                        logging.info(f"New item added to DB. Redeye ID: {redeye_id}, table: {table}")

                        if "sale" in url and "Out Of Stock" in status:
                            logging.info(f"Redeye ID: {redeye_id}, table: {table} is out of stock. Ignore it")
                            continue

                        data = {
                            "redeye_id": redeye_id,
                            "table": self.parser_json[genre][section]["table"]
                        }
                        request = requests.post(f"{API_HOST}/new_release", json=data, headers=api_key_headers)
                        if request.status_code != 200:
                            logging.warning(f"Can't reach API! Status code: {request.status_code}")

        db_connection.close()
        logging.info(f"========== Session ended at {datetime.now(timezone.utc)} ==========")
