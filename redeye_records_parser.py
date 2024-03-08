#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import os
import logging

from time import sleep

from config import basedir, PARSER_COOL_DOWN
from app.parser import Parser


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        filename=os.path.join(basedir, "redeye_records_parser.log"),
        filemode="w",
        format="%(asctime)s %(levelname)s %(message)s"
    )

    p = Parser()
    try:
        p.db_initiation()
        while True:
            sleep(PARSER_COOL_DOWN)
            p.check_new_releases()
    except Exception as e:
        logging.critical(e)
