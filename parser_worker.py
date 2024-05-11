#!/usr/bin/python

import os
import logging

from config import basedir
from app.parser import Parser


def main(p):
    try:
        p.check_new_releases()
    except Exception as e:
        logging.critical(e)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        filename=os.path.join(basedir, "parser_worker.log"),
        filemode="a",
        format="%(asctime)s %(levelname)s %(message)s"
    )

    parser = Parser()
    main(parser)
