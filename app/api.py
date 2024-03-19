#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import re
import logging
from functools import wraps
from datetime import datetime, timezone

import telebot
import sqlite3
from telebot.apihelper import ApiException
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import request, Blueprint
from flask_restx import Api, Resource, fields

from config import BOT_TOKEN, API_KEY, DB_PATH, genres


bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
blueprint = Blueprint("api", __name__, url_prefix="/api")
api = Api(app=blueprint, version="1", title="Redeye Records Bot API")
api = api.namespace("v1")
responses = {
    200: "OK",
    201: "Created",
    401: "Unauthorized",
    500: "Internal Server Error"
}


def require_api_key(view_function):
    @wraps(view_function)
    def decorated_route(*args, **kwargs):
        if request.headers.get("x-api-key") and request.headers.get("x-api-key") == API_KEY:
            return view_function(*args, **kwargs)
        else:
            api.abort(401)
    return decorated_route


@api.route("/start")
class Start(Resource):
    @api.doc(
        responses={
            200: "OK",
            201: "Created",
            401: "Unauthorized",
            500: "Internal Server Error"
        },
        body=api.model(
            "Register new user",
            {
                "user_chat_id": fields.Integer(
                    description="User's Telegram chat ID",
                    required=True
                ),
                "username": fields.String(
                    description="User's username",
                    required=False
                ),
                "first_name": fields.String(
                    description="User's first name",
                    required=False
                ),
                "last_name": fields.String(
                    description="User's last name",
                    required=False
                )
            }
        ),
        params={
            "x-api-key": {
                "in": "header",
                "description": "API key",
                "type": "string",
                "required": "true"
            }
        }
    )
    @require_api_key
    def put(self):
        """Register new user"""
        try:
            user_chat_id = request.json["user_chat_id"]
            username = request.json["username"]
            first_name = request.json["first_name"]
            last_name = request.json["last_name"]
            logging.info(f"New user! user chat id: {user_chat_id}, username: {username}")
            db_connection = sqlite3.connect(DB_PATH)
            db_cursor = db_connection.cursor()
            db_cursor.execute(
                f"""
                    SELECT user_id FROM users WHERE user_chat_id = {user_chat_id}
                ;
                """
            )
            user_id = bool(db_cursor.fetchone())
            if not user_id:
                db_cursor.execute(
                    f"""
                        INSERT INTO users (user_id, user_chat_id, username, first_name, last_name, is_active, registered_at)
                        VALUES ((SELECT count(user_id) FROM users) + 1, ?, ?, ?, ?, true, ?)
                    ;
                    """, (user_chat_id, username, first_name, last_name, str(datetime.now(timezone.utc)))
                )
                db_connection.commit()
                db_cursor.execute(
                    f"""
                        INSERT INTO subscriptions VALUES
                        ((SELECT user_id FROM users WHERE user_chat_id = {user_chat_id}),
                        false, false, false, false, false, false, false, false, false)
                    ;
                    """
                )
                db_connection.commit()
                status_code = 201
                additional_info = ""
            else:
                db_cursor.execute(
                    f"""
                        UPDATE users
                        SET username = ?,
                            first_name = ?,
                            last_name = ?,
                            is_active = true
                        WHERE user_chat_id = {user_chat_id}
                    ;
                    """, (username, first_name, last_name)
                )
                db_connection.commit()
                db_cursor.execute(
                    f"""
                        UPDATE subscriptions
                        SET bass_music = false,
                            drum_bass_jungle = false,
                            ambient_experimental_drone = false,
                            hip_hop_soul_jazz_funk = false,
                            house_disco = false,
                            reggae = false,
                            techno_electro = false,
                            balearic_downtempo = false,
                            alternative_indie_folk_punk = false
                        WHERE user_id = (SELECT user_id FROM users WHERE user_chat_id = ?)
                    ;
                    """, (user_chat_id,)
                )
                db_connection.commit()

                status_code = 200
                additional_info = f". User {user_chat_id} already exists. All subscriptions removed"

            db_connection.close()

            return responses[status_code] + additional_info, status_code

        except Exception as e:
            api.abort(500, e.__doc__, status=responses[500], status_сode=500)


@api.route("/subscribe")
class Subscribe(Resource):
    @api.doc(
        responses={
            200: "OK",
            401: "Unauthorized",
            500: "Internal Server Error"
        },
        body=api.model(
            "Set up user's subscriptions",
            {
                "user_chat_id": fields.Integer(
                    description="User's Telegram chat ID",
                    required=True
                ),
                "genre": fields.String(
                    description="Genre to follow",
                    required=True
                )
            }
        ),
        params={
            "x-api-key": {
                "in": "header",
                "description": "API key",
                "type": "string",
                "required": "true"
            }
        }
    )
    @require_api_key
    def put(self):
        """Set up user's subscriptions"""
        try:
            user_chat_id = request.json["user_chat_id"]
            genre = request.json["genre"]
            db_connection = sqlite3.connect(DB_PATH)
            db_cursor = db_connection.cursor()
            db_cursor.execute(
                f"""
                    UPDATE subscriptions
                    SET {genre} = true
                    WHERE user_id = (SELECT user_id FROM users WHERE user_chat_id = ?)
                ;
                """, (user_chat_id,)
            )
            db_connection.commit()
            db_connection.close()

            status_code = 200

            return f"{responses[status_code]}. Subscribed to {genres[genre]}", status_code

        except Exception as e:
            api.abort(500, e.__doc__, status=responses[500], status_сode=500)


@api.route("/unsubscribe")
class Unsubscribe(Resource):
    @api.doc(
        responses={
            200: "OK",
            401: "Unauthorized",
            500: "Internal Server Error"
        },
        body=api.model(
            "Unsubscribe from all threads",
            {
                "user_chat_id": fields.Integer(
                    description="User's Telegram chat ID",
                    required=True
                )
            }
        ),
        params={
            "x-api-key": {
                "in": "header",
                "description": "API key",
                "type": "string",
                "required": "true"
            }
        }
    )
    @require_api_key
    def put(self):
        """Unsubscribe from all threads"""
        try:
            user_chat_id = request.json["user_chat_id"]
            db_connection = sqlite3.connect(DB_PATH)
            db_cursor = db_connection.cursor()
            db_cursor.execute(
                f"""
                    UPDATE subscriptions
                    SET bass_music = false,
                        drum_bass_jungle = false,
                        ambient_experimental_drone = false,
                        hip_hop_soul_jazz_funk = false,
                        house_disco = false,
                        reggae = false,
                        techno_electro = false,
                        balearic_downtempo = false,
                        alternative_indie_folk_punk = false
                    WHERE user_id = (SELECT user_id FROM users WHERE user_chat_id = ?)
                ;
                """, (user_chat_id,)
            )
            db_connection.commit()
            db_connection.close()

            status_code = 200

            return f"{responses[status_code]}. Subscriptions were deleted", status_code

        except Exception as e:
            api.abort(500, e.__doc__, status=responses[500], status_сode=500)


@api.route("/my_subscriptions")
class MySubscriptions(Resource):
    @api.doc(
        responses={
            200: "OK",
            401: "Unauthorized",
            500: "Internal Server Error"
        },
        params={
            "user_chat_id": {
                "in": "query",
                "description": "User's Telegram chat ID",
                "type": "integer",
                "required": "true"
            },
            "x-api-key": {
                "in": "header",
                "description": "API key",
                "type": "string",
                "required": "true"
            }
        }
    )
    @require_api_key
    def get(self):
        """User's subscriptions info"""
        try:
            user_chat_id = request.args["user_chat_id"]
            db_connection = sqlite3.connect(DB_PATH)
            db_cursor = db_connection.cursor()
            db_cursor.execute(
                """
                    SELECT bass_music,
                           drum_bass_jungle,
                           ambient_experimental_drone,
                           hip_hop_soul_jazz_funk,
                           house_disco,
                           reggae,
                           techno_electro,
                           balearic_downtempo,
                           alternative_indie_folk_punk
                    FROM subscriptions
                    WHERE user_id = (SELECT user_id FROM users WHERE user_chat_id = ?)
                ;
                """, (user_chat_id,)
            )
            subscriptions = db_cursor.fetchone()
            db_connection.close()

            result = dict()
            counter = 0
            for genre in genres:
                result[genres[genre]] = subscriptions[counter]
                counter += 1

            return result, 200

        except Exception as e:
            api.abort(500, e.__doc__, status=responses[500], status_сode=500)


@api.route("/new_release")
class NewRelease(Resource):
    @api.doc(
        responses={
            200: "OK",
            401: "Unauthorized",
            500: "Internal Server Error"
        },
        body=api.model(
            "API waits for new release notification from parser",
            {
                "redeye_id": fields.Integer(
                    description="Release's Redeye ID",
                    required=True
                ),
                "table": fields.String(
                    description="Table where release info was stored",
                    required=True
                )
            }
        ),
        params={
            "x-api-key": {
                "in": "header",
                "description": "API key",
                "type": "string",
                "required": "true"
            }
        }
    )
    @require_api_key
    def post(self):
        """API waits for new release notification from parser"""
        try:
            redeye_id = request.json["redeye_id"]
            table = request.json["table"]
            logging.debug(f"New release - redeye_id: {redeye_id}, table: {table}")

            db_connection = sqlite3.connect(DB_PATH)
            db_cursor = db_connection.cursor()
            db_cursor.execute(
                f"""
                    SELECT title, cat, tracklist, price, release_url, samples, genre, section FROM {table} WHERE redeye_id = ?
                ;
                """, (redeye_id,)
            )
            title, cat, tracklist, price, release_url, samples, genre, section = db_cursor.fetchone()
            release = f"*{genre.upper()}*\n{section.upper()}\n\n{title}\n_{cat}_\n\n{tracklist}\n\n{price}\n{release_url}"

            db_cursor.execute(
                f"""
                    SELECT users.user_chat_id
                    FROM users
                    JOIN subscriptions ON subscriptions.user_id = users.user_id
                    WHERE subscriptions.{re.sub(r" / |-| & |\s+|% ", "_", genre).lower()} = true AND users.is_active = true
                ;
                """
            )
            users = [user_chat_id[0] for user_chat_id in db_cursor.fetchall()]
            logging.debug(f"Users found: {users}")

            if not bool(users):
                pass
            else:
                reply_markup = None
                if bool(samples):
                    samples = samples.split(",")
                    count = len(samples)
                    if count == 1:
                        reply_markup = InlineKeyboardMarkup()
                        button_a = InlineKeyboardButton(text="PLAY A", url=samples[0])
                        reply_markup.add(button_a)
                    if count == 2:
                        reply_markup = InlineKeyboardMarkup(row_width=2)
                        button_a = InlineKeyboardButton(text="PLAY A", url=samples[0])
                        button_b = InlineKeyboardButton(text="PLAY B", url=samples[1])
                        reply_markup.add(button_a, button_b)
                    if count == 3:
                        reply_markup = InlineKeyboardMarkup(row_width=3)
                        button_a = InlineKeyboardButton(text="PLAY A", url=samples[0])
                        button_b = InlineKeyboardButton(text="PLAY B", url=samples[1])
                        button_c = InlineKeyboardButton(text="PLAY C", url=samples[2])
                        reply_markup.add(button_a, button_b, button_c)
                    if count == 4:
                        reply_markup = InlineKeyboardMarkup(row_width=4)
                        button_a = InlineKeyboardButton(text="PLAY A", url=samples[0])
                        button_b = InlineKeyboardButton(text="PLAY B", url=samples[1])
                        reply_markup.add(button_a, button_b)
                        button_c = InlineKeyboardButton(text="PLAY C", url=samples[2])
                        button_d = InlineKeyboardButton(text="PLAY D", url=samples[3])
                        reply_markup.add(button_c, button_d)

                for user_chat_id in users:
                    try:
                        logging.debug(f"Sending release to user chat id: {user_chat_id}")
                        bot.send_message(user_chat_id, release, reply_markup=reply_markup, parse_mode="Markdown")
                    except ApiException as e:
                        if "bot was blocked by the user" in e.args[0]:
                            db_cursor.execute(
                                """
                                    UPDATE users
                                    SET is_active = false
                                    WHERE user_chat_id = ?
                                ;
                                """, (user_chat_id,)
                            )
                            db_connection.commit()

            db_connection.close()

            status_code = 200

            return responses[status_code], status_code

        except Exception as e:
            api.abort(500, e.__doc__, status=responses[500], status_сode=500)


@api.route("/stats")
class Stats(Resource):
    @api.doc(
        responses={
            200: "OK",
            401: "Unauthorized",
            500: "Internal Server Error"
        },
        params={
            "x-api-key": {
                "in": "header",
                "description": "API key",
                "type": "string",
                "required": "true"
            }
        }
    )
    @require_api_key
    def get(self):
        """Users statistics"""
        try:
            db_connection = sqlite3.connect(DB_PATH)
            db_cursor = db_connection.cursor()
            db_cursor.execute(
                """
                    SELECT t1.users_active, 
                           t2.users_total
                    FROM
                    (SELECT count(is_active) AS users_active FROM users WHERE is_active = true) AS t1,
                    (SELECT count(user_id) AS users_total FROM users) AS t2
                ;
                """
            )
            users = db_cursor.fetchone()

            query = "SELECT "
            for n in range(len(genres)):
                query += f"t{n + 1}.{list(genres.keys())[n]}_subs_active, "
            for n in range(len(genres)):
                query += f"t{len(genres) + n + 1}.{list(genres.keys())[n]}_subs_total{", " if n != len(genres) - 1 else " "}"
            query += "FROM "
            for n in range(len(genres)):
                query += f"(SELECT count(u.user_id) AS {list(genres.keys())[n]}_subs_active FROM users u JOIN subscriptions s on u.user_id = s.user_id WHERE u.is_active = true AND {list(genres.keys())[n]} = true) AS t{n + 1}, "
            for n in range(len(genres)):
                query += f"(SELECT count(*) AS {list(genres.keys())[n]}_subs_total FROM subscriptions WHERE {list(genres.keys())[n]} = true) AS t{len(genres) + n + 1}{", " if n != len(genres) - 1 else ";"}"
            db_cursor.execute(query)
            subs = db_cursor.fetchone()
            db_connection.close()
            stats = f"*users*: active {users[0]}, total {users[1]}\n"
            for i in range(int(len(subs) / 2)):
                stats += f"\n*{list(genres.keys())[i]}*: active {subs[i]}, total {subs[int(len(subs) / 2) + i]}"

            return stats, 200

        except Exception as e:
            api.abort(500, e.__doc__, status=responses[500], status_сode=500)


@api.route("/help")
class Help(Resource):
    @api.doc(
        responses={
            200: "OK",
            401: "Unauthorized",
            500: "Internal Server Error"
        },
        params={
            "x-api-key": {
                "in": "header",
                "description": "API key",
                "type": "string",
                "required": "true"
            }
        }
    )
    @require_api_key
    def get(self):
        """A list of available actions"""
        help_text = "🌐 *redeyerecords.co.uk* — dance music specialists since 1992\n\n" \
                    "*/selections* to choose selections\n\n" \
                    "*/my_subscriptions* to get a list of your subscriptions\n\n" \
                    "*/unsubscribe* to unsubscribe"
        try:
            return help_text, 200

        except Exception as e:
            api.abort(500, e.__doc__, status=responses[500], status_сode=500)
