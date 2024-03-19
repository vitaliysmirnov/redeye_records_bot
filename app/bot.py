#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import requests

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from flask import Flask, request, render_template

from config import BOT_TOKEN, ADMIN_CHAT_ID, API_HOST, APP_HOST, api_key_headers, genres
from app.api import blueprint


bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)
app.register_blueprint(blueprint)


@app.route("/")
def index():
    """index page"""
    return render_template("index.html")


@app.route("/" + BOT_TOKEN, methods=["POST"])
def get_message():
    """Webhook routing: new messages processor"""
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@bot.message_handler(commands=["start"])
def command_start(message):
    """/start command handler"""
    message_text = f"Hi *{message.from_user.first_name}*!"
    bot.send_message(message.from_user.id, message_text, parse_mode="Markdown")
    #  user's data collection
    user_chat_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    #  send user's data to API
    data = {
        "user_chat_id": user_chat_id,
        "username": username,
        "first_name": first_name,
        "last_name": last_name
    }
    response = requests.put(f"{API_HOST}/start", json=data, headers=api_key_headers)
    #  introduce_text depended on API response
    if response.status_code in (200, 201):
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
    buttons = [InlineKeyboardButton(genres[genre], callback_data=genre) for genre in genres]
    buttons.append(InlineKeyboardButton("unsubscribe", callback_data="unsubscribe"))
    reply_markup.add(*buttons)
    message_text = "Tap on genres you want to follow"
    #  response
    bot.send_message(user_chat_id, message_text, reply_markup=reply_markup, parse_mode="Markdown", disable_notification=True)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    """/selections callback handler"""
    #  get user_chat_id from message to identify user
    user_chat_id = call.from_user.id
    #  result depended on clicked button
    data = {
        "user_chat_id": user_chat_id
    }
    if call.data == "unsubscribe":
        response = requests.put(f"{API_HOST}/unsubscribe", json=data, headers=api_key_headers)
    else:
        data["genre"] = call.data
        response = requests.put(f"{API_HOST}/subscribe", json=data, headers=api_key_headers)
    #  response
    bot.answer_callback_query(call.id, response.json())


@bot.message_handler(commands=["unsubscribe"])
def command_unsubscribe(message):
    """/unsubscribe command handler"""
    bot.send_message(message.from_user.id, "Give me a second...")
    #  get user_chat_id from message to identify user
    user_chat_id = message.chat.id
    #  use API method to start command execution
    data = {
        "user_chat_id": user_chat_id
    }
    requests.put(f"{API_HOST}/unsubscribe", json=data, headers=api_key_headers)
    #  menu buttons
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        KeyboardButton("/help"),
        KeyboardButton("/selections"),
    )
    #  response
    bot.send_message(user_chat_id, "You can renew your subscriptions at */selections*", reply_markup=keyboard, parse_mode="Markdown")


@bot.message_handler(commands=["my_subscriptions"])
def command_my_subscriptions(message):
    """/my_subscriptions command handler"""
    #  get user_chat_id from message to identify user
    user_chat_id = message.chat.id
    response = requests.get(f"{API_HOST}/my_subscriptions?user_chat_id={user_chat_id}", headers=api_key_headers)
    #  menu buttons
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    #  result depended on API response
    my_subscriptions = list()
    if response.status_code == 200:
        for key, value in response.json().items():
            if value:
                my_subscriptions.append(f"*{key}*")
        #  info message depended on user's subscriptions
        if bool(my_subscriptions):
            result = "You're subscribed to\n\n" + "\n".join(my_subscriptions)
            keyboard.add(
                KeyboardButton("/help"),
                KeyboardButton("/selections"),
                KeyboardButton("/unsubscribe")
            )
        else:
            result = "You're not subscribed to anything yet"
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
    if user_chat_id == ADMIN_CHAT_ID:
        #  use API method to start command execution
        response = requests.get(f"{API_HOST}/stats", headers=api_key_headers)
        #  response
        bot.send_message(user_chat_id, response.json(), parse_mode="Markdown")


@bot.message_handler(commands=["help"])
def command_help(message):
    """/help command handler"""
    #  get user_chat_id from message to identify user
    user_chat_id = message.chat.id
    #  text
    response = requests.get(f"{API_HOST}/help", headers=api_key_headers)
    #  response
    bot.send_message(user_chat_id, response.json(), parse_mode="Markdown", disable_notification=True)


if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=APP_HOST + BOT_TOKEN)
