FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY bot bot/
COPY database database/
COPY models models/
COPY notifier notifier/

ENV PYTHONPATH /app

ENTRYPOINT [ "python" ]
CMD [ "bot/events_bot.py" ]