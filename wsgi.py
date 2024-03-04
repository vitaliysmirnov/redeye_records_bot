#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

from app.api import app
from app.config import HOST

if __name__ == "__main__":
    app.run(host=HOST)
