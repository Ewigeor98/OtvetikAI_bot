FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
COPY bot.py /app/bot.py

RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["python", "/app/bot.py"]
