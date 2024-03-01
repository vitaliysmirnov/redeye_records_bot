#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import requests

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup

from app.config import *


bot = telebot.TeleBot(BOT_TOKEN, threaded=False)


@bot.message_handler(commands=["start"])
def command_start(message):
    """/start command handler"""
    message_text = f"Hi *{message.from_user.first_name}*!\n\n"\
                   "This bot can send you notifications when new items appear at Redeye Records"
    bot.send_message(message.from_user.id, message_text, parse_mode="Markdown")
    #  user's data collection
    user_chat_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    data = {
        "user_chat_id": user_chat_id,
        "username": username,
        "first_name": first_name,
        "last_name": last_name
    }
    #  send user's data to API
    response = requests.post(f"{API_HOST}/start", json=data)
    #  introduce_text depended on API response
    if response == 201 or 204:
        message_text = "Use */selections* to choose genres you want to follow"
    else:
        message_text = "Bot is on maintenance mode. Try again later"
    #  menu buttons
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        KeyboardButton("/help"),
        KeyboardButton("/selections")
    )
    #  response
    bot.send_message(user_chat_id, message_text, reply_markup=keyboard, parse_mode="Markdown")


@bot.message_handler(commands=["selections"])
def command_selections(message):
    """/selections command handler"""
    #  get user_chat_id from message to identify user
    user_chat_id = message.chat.id
    #  menu buttons
    reply_markup = InlineKeyboardMarkup()
    reply_markup.row_width = 1
    reply_markup.add(
        InlineKeyboardButton("BASS MUSIC", callback_data="bass_music"),
        InlineKeyboardButton("DRUM & BASS • JUNGLE", callback_data="drum_and_bass"),
        InlineKeyboardButton("AMBIENT • EXPERIMENTAL • DRONE", callback_data="experimental"),
        InlineKeyboardButton("HIP HOP • SOUL • JAZZ • FUNK", callback_data="funk_hip_hop_soul"),
        InlineKeyboardButton("HOUSE • DISCO", callback_data="house_disco"),
        InlineKeyboardButton("REGGAE", callback_data="reggae"),
        InlineKeyboardButton("TECHNO • ELECTRO", callback_data="techno_electro"),
        InlineKeyboardButton("BALEARIC • DOWNTEMPO", callback_data="balearic_and_downtempo"),
        InlineKeyboardButton("ALTERNATIVE / INDIE / FOLK / PUNK", callback_data="alternative_indie_folk_punk"),
        InlineKeyboardButton("unsubscribe", callback_data="unsub")
    )
    message_text = "Tap on selections you want to follow"
    #  response
    bot.send_message(user_chat_id, message_text, reply_markup=reply_markup, parse_mode="Markdown", disable_notification=True)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    """/selections callback handler"""
    #  get user_chat_id from message to identify user
    user_chat_id = call.from_user.id
    #  result depended on clicked button
    if call.data == "unsub":
        response = requests.put(f"{API_HOST}/unsub?user_chat_id={user_chat_id}")
    else:
        selection = call.data
        response = requests.put(f"{API_HOST}/subscribe?user_chat_id={user_chat_id}&selection={selection}")
    result = response.json()["message"]["result"]
    #  response
    bot.answer_callback_query(call.id, result)


@bot.message_handler(commands=["unsub"])
def command_unsub(message):
    """/unsub command handler"""
    bot.send_message(message.from_user.id, "Give me a second...")
    #  get user_chat_id from message to identify user
    user_chat_id = message.chat.id
    #  use API method to start command execution
    response = requests.put(f"{API_HOST}/unsub?user_chat_id={user_chat_id}")
    result = response.json()["message"]["result"]
    #  menu buttons
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        KeyboardButton("/help"),
        KeyboardButton("/selections"),
    )
    #  response
    bot.send_message(user_chat_id, result.replace("/selections", "*/selections*"), reply_markup=keyboard, parse_mode="Markdown")


@bot.message_handler(commands=["help"])
def command_help(message):
    """/help command handler"""
    #  get user_chat_id from message to identify user
    user_chat_id = message.chat.id
    #  text
    help_text = "*redeyerecords.co.uk* - dance music specialists since 1992\n\n\n" \
                "*/selections* to choose selections\n\n" \
                "*/mysubs* to get your subs\n\n" \
                "*/unsub* to unsubscribe\n\n"
    #  response
    bot.send_message(user_chat_id, help_text, parse_mode="Markdown", disable_notification=True)


@bot.message_handler(commands=["mysubs"])
def command_mysubs(message):
    """/mysubs command handler"""
    bot.send_message(message.from_user.id, "Give me a second...")
    #  get user_chat_id from message to identify user
    user_chat_id = message.chat.id
    response = requests.get(f"{API_HOST}/mysubs?user_chat_id={user_chat_id}")
    #  menu buttons
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    #  result depended on API response
    mysubs = list()
    if response.status_code == 200:
        result = response.json()["message"]["result"]
        for key, value in result.items():
            if value:
                mysubs.append(key)
        #  info message depended on user's subscriptions
        if bool(mysubs):
            result = "You are subscribed to\n" + "\n".join(mysubs)
            keyboard.add(
                KeyboardButton("/help"),
                KeyboardButton("/selections"),
                KeyboardButton("/unsub")
            )
        else:
            result = "You are not subscribed to anything yet"
            keyboard.add(
                KeyboardButton("/help"),
                KeyboardButton("/selections")
            )
    else:
        result = "There is an error. Please try again later."
    #  response
    bot.send_message(user_chat_id, result, reply_markup=keyboard, parse_mode="Markdown", disable_notification=True)


@bot.message_handler(commands=["stats"])
def command_stats(message):
    """/stats command handler"""
    #  get user_chat_id from message to identify user
    user_chat_id = message.chat.id
    #  use API method to start command execution
    response = requests.get(f"{API_HOST}/stats?admin_chat_id={ADMIN_CHAT_ID}&telegram_api_token={BOT_TOKEN}")
    #  result depended on API response
    if response.status_code == 200:
        result = response.json()["message"]["result"]
        stats = f"*USERS*: active {result['users']['users_active']}, total {result['users']['users_total']}\n\n" \
                f"*BASS MUSIC*: active {result['subs']['bass_music_subs_active']}, total {result['subs']['bass_music_subs_total']}\n" \
                f"*DRUM & BASS • JUNGLE*: active {result['subs']['drum_and_bass_subs_active']}, total {result['subs']['drum_and_bass_subs_total']}\n" \
                f"*AMBIENT • EXPERIMENTAL • DRONE*: active {result['subs']['experimental_subs_active']}, total {result['subs']['experimental_subs_total']}\n" \
                f"*HIP HOP • SOUL • JAZZ • FUNK*: active {result['subs']['funk_hip_hop_soul_subs_active']}, total {result['subs']['funk_hip_hop_soul_subs_total']}\n" \
                f"*HOUSE • DISCO*: active {result['subs']['house_disco_subs_active']}, total {result['subs']['house_disco_subs_total']}\n" \
                f"*REGGAE*: active {result['subs']['reggae_subs_active']}, total {result['subs']['reggae_subs_total']}\n" \
                f"*TECHNO • ELECTRO*: active {result['subs']['techno_electro_subs_active']}, total {result['subs']['techno_electro_subs_total']}\n" \
                f"*BALEARIC • DOWNTEMPO*: active {result['subs']['balearic_and_downtempo_subs_active']}, total {result['subs']['balearic_and_downtempo_subs_total']}\n" \
                f"*ALTERNATIVE / INDIE / FOLK / PUNK*: active {result['subs']['alternative_indie_folk_punk_subs_active']}, total {result['subs']['alternative_indie_folk_punk_subs_total']}\n"
    else:
        stats = f"There is an error. API status code: {response.status_code}"
    #  response
    bot.send_message(user_chat_id, stats, parse_mode="Markdown")


if __name__ == "__main__":
    bot.polling(non_stop=True)

    # bot.remove_webhook()
    # bot.set_webhook(url=APP_HOST + API_TOKEN)
