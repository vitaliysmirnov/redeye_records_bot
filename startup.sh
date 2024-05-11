#!/bin/bash
python database_setup.py &&\
python database_initiation.py &&\
cron &&\
python set_webhook.py &&\
uwsgi --ini redeye_records_bot.ini