#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import requests
from app.config import *

user_chat_id = 230217326
selection = "bass_music"

requests.put(f"{API_HOST}/subscribe?user_chat_id={user_chat_id}&selection={selection}")
