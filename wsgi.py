#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import logging

from app.bot import app

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename="redeye_records_bot.log", filemode="w", format="%(asctime)s %(levelname)s %(message)s")

    app.run()
