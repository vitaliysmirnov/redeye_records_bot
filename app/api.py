#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import logging
from functools import wraps
from datetime import datetime, timezone

import telebot
import sqlite3
from telebot.apihelper import ApiException
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import request, Blueprint
from flask_restx import Api, Resource, fields

from config import BOT_TOKEN, API_KEY, DB_PATH, selections


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
                            drum_and_bass = false,
                            experimental = false,
                            funk_hip_hop_soul = false,
                            house_disco = false,
                            reggae = false,
                            techno_electro = false,
                            balearic_and_downtempo = false,
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
                "selection": fields.String(
                    description="Selection to follow",
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
            selection = request.json["selection"]
            db_connection = sqlite3.connect(DB_PATH)
            db_cursor = db_connection.cursor()
            db_cursor.execute(
                f"""
                    UPDATE subscriptions
                    SET {selection} = true
                    WHERE user_id = (SELECT user_id FROM users WHERE user_chat_id = ?)
                ;
                """, (user_chat_id,)
            )
            db_connection.commit()
            db_connection.close()

            status_code = 200

            return f"{responses[status_code]}. Subscribed to {selections[selection]}", status_code

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
                        drum_and_bass = false,
                        experimental = false,
                        funk_hip_hop_soul = false,
                        house_disco = false,
                        reggae = false,
                        techno_electro = false,
                        balearic_and_downtempo = false,
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
                           drum_and_bass,
                           experimental,
                           funk_hip_hop_soul,
                           house_disco,
                           reggae,
                           techno_electro,
                           balearic_and_downtempo,
                           alternative_indie_folk_punk
                    FROM subscriptions
                    WHERE user_id = (SELECT user_id FROM users WHERE user_chat_id = ?)
                ;
                """, (user_chat_id,)
            )
            subscriptions = db_cursor.fetchone()
            db_connection.close()

            selections_l = list(selections.keys())
            result_raw = dict()
            for i in range(len(selections_l)):
                result_raw[selections_l[i]] = subscriptions[i]
            result = dict()

            result["BASS MUSIC"] = result_raw.pop("bass_music")
            result["DRUM & BASS • JUNGLE"] = result_raw.pop("drum_and_bass")
            result["AMBIENT • EXPERIMENTAL • DRONE"] = result_raw.pop("experimental")
            result["HIP HOP • SOUL • JAZZ • FUNK"] = result_raw.pop("funk_hip_hop_soul")
            result["HOUSE • DISCO"] = result_raw.pop("house_disco")
            result["REGGAE"] = result_raw.pop("reggae")
            result["TECHNO • ELECTRO"] = result_raw.pop("techno_electro")
            result["BALEARIC • DOWNTEMPO"] = result_raw.pop("balearic_and_downtempo")
            result["ALTERNATIVE / INDIE / FOLK / PUNK"] = result_raw.pop("alternative_indie_folk_punk")

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
                    SELECT item, samples, selection FROM {table} WHERE redeye_id = ?
                ;
                """, (redeye_id,)
            )
            item, samples, selection = db_cursor.fetchone()

            db_cursor.execute(
                f"""
                    SELECT users.user_chat_id
                    FROM users
                    JOIN subscriptions ON subscriptions.user_id = users.user_id
                    WHERE subscriptions.{selection} = true AND users.is_active = true
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
                    else:
                        pass

                for user_chat_id in users:
                    try:
                        logging.debug(f"Sending release to user chat id: {user_chat_id}")
                        bot.send_message(user_chat_id, item, reply_markup=reply_markup, parse_mode="Markdown")
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
            db_cursor.execute(
                """
                    SELECT t1.bass_music_subs_active, 
                           t2.drum_and_bass_subs_active, 
                           t3.experimental_subs_active, 
                           t4.funk_hip_hop_soul_subs_active, 
                           t5.house_disco_subs_active, 
                           t6.reggae_subs_active,
                           t7.techno_electro_subs_active,
                           t8.balearic_and_downtempo_subs_active,
                           t9.alternative_indie_folk_punk_subs_active,
                           t10.bass_music_subs_total, 
                           t11.drum_and_bass_subs_total, 
                           t12.experimental_subs_total, 
                           t13.funk_hip_hop_soul_subs_total, 
                           t14.house_disco_subs_total, 
                           t15.reggae_subs_total, 
                           t16.techno_electro_subs_total, 
                           t17.balearic_and_downtempo_subs_total, 
                           t18.alternative_indie_folk_punk_subs_total
                    FROM
                    (SELECT count(u.user_id) AS bass_music_subs_active FROM users u JOIN subscriptions s on u.user_id = s.user_id 
                        WHERE u.is_active = true AND bass_music = true) AS t1,
                    (SELECT count(u.user_id) AS drum_and_bass_subs_active FROM users u JOIN subscriptions s on u.user_id = s.user_id 
                        WHERE u.is_active = true AND drum_and_bass = true) AS t2,
                    (SELECT count(u.user_id) AS experimental_subs_active FROM users u JOIN subscriptions s on u.user_id = s.user_id 
                        WHERE u.is_active = true AND experimental = true) AS t3,
                    (SELECT count(u.user_id) AS funk_hip_hop_soul_subs_active FROM users u JOIN subscriptions s on u.user_id = s.user_id 
                        WHERE u.is_active = true AND funk_hip_hop_soul = true) AS t4,
                    (SELECT count(u.user_id) AS house_disco_subs_active FROM users u JOIN subscriptions s on u.user_id = s.user_id 
                        WHERE u.is_active = true AND house_disco = true) AS t5,
                    (SELECT count(u.user_id) AS reggae_subs_active FROM users u JOIN subscriptions s on u.user_id = s.user_id 
                        WHERE u.is_active = true AND reggae = true) AS t6,
                    (SELECT count(u.user_id) AS techno_electro_subs_active FROM users u JOIN subscriptions s on u.user_id = s.user_id 
                        WHERE u.is_active = true AND techno_electro = true) AS t7,
                    (SELECT count(u.user_id) AS balearic_and_downtempo_subs_active FROM users u JOIN subscriptions s on u.user_id = s.user_id 
                        WHERE u.is_active = true AND balearic_and_downtempo = true) AS t8,
                    (SELECT count(u.user_id) AS alternative_indie_folk_punk_subs_active FROM users u JOIN subscriptions s on u.user_id = s.user_id 
                        WHERE u.is_active = true AND alternative_indie_folk_punk = true) AS t9,
                    (SELECT count(*) AS bass_music_subs_total FROM subscriptions WHERE bass_music = true) AS t10,
                    (SELECT count(*) AS drum_and_bass_subs_total FROM subscriptions WHERE drum_and_bass = true) AS t11,
                    (SELECT count(*) AS experimental_subs_total FROM subscriptions WHERE experimental = true) AS t12,
                    (SELECT count(*) AS funk_hip_hop_soul_subs_total FROM subscriptions WHERE funk_hip_hop_soul = true) AS t13,
                    (SELECT count(*) AS house_disco_subs_total FROM subscriptions WHERE house_disco = true) AS t14,
                    (SELECT count(*) AS reggae_subs_total FROM subscriptions WHERE reggae = true) AS t15,
                    (SELECT count(*) AS techno_electro_subs_total FROM subscriptions WHERE techno_electro = true) AS t16,
                    (SELECT count(*) AS balearic_and_downtempo_subs_total FROM subscriptions WHERE balearic_and_downtempo = true) AS t17,
                    (SELECT count(*) AS alternative_indie_folk_punk_subs_total FROM subscriptions WHERE alternative_indie_folk_punk = true) AS t18
                ;
                """
            )
            subs = db_cursor.fetchone()
            db_connection.close()
            stats = f"*users*: active {users[0]}, total {users[1]}\n"
            for i in range(int(len(subs) / 2)):
                stats += f"\n*{list(selections.keys())[i]}*: active {subs[i]}, total {subs[int(len(subs) / 2) + i]}"

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
                    "*/my_subscriptions* to get your subscriptions\n\n" \
                    "*/unsubscribe* to unsubscribe"
        try:
            return help_text, 200

        except Exception as e:
            api.abort(500, e.__doc__, status=responses[500], status_сode=500)
