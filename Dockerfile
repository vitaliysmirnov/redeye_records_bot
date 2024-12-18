FROM python:3.9
RUN apt-get update && apt-get install cron -y
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY crontab /etc/cron.d/crontab
COPY startup.sh /app
COPY . /app
RUN chmod 0644 /etc/cron.d/crontab
RUN chmod a+x parser_worker.py
RUN crontab /etc/cron.d/crontab
CMD ["/bin/bash", "-c", "./startup.sh"]