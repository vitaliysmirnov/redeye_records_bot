#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import logging

from app.parser import run_parser
from app.config import *



logging.basicConfig(level=logging.INFO,
                    filename="redeye_records_bot.log",
                    filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")


if __name__ == "__main__":
    run_parser()
