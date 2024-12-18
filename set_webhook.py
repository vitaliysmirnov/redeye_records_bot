#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import os
import logging

from app.bot import bot
from config import basedir, APP_HOST, BOT_TOKEN


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        # filename=os.path.join(basedir, "set_webhook.log"),
        # filemode="a",
        format="[%(filename)s] %(asctime)s %(levelname)s %(message)s"
    )

    bot.remove_webhook()
    bot.set_webhook(url=APP_HOST + BOT_TOKEN)
    logging.info(f"Webhook for {BOT_TOKEN} was set on {APP_HOST + BOT_TOKEN}")
