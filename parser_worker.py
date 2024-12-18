#!/usr/bin/python

import os
import logging
from logging.handlers import TimedRotatingFileHandler

from config import basedir
from app.parser import Parser


def main(p):
    try:
        p.check_new_releases()
    except Exception as e:
        logging.critical(e)


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = TimedRotatingFileHandler(os.path.join(basedir, "parser_worker.log"), when="midnight", backupCount=10)
    formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    parser = Parser()
    main(parser)
