#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import os
import logging

from config import basedir
from app.parser import Parser


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        # filename=os.path.join(basedir, "database_initiation.log"),
        # filemode="a",
        format="[%(filename)s] %(asctime)s %(levelname)s %(message)s"
    )

    parser = Parser(init=True)
    parser.db_initiation()
