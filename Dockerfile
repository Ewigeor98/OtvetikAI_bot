FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN ls -la /app
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "/app/bot.py"]
