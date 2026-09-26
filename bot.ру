import os
import telebot

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "👋 Привет! Я OtvetikAI 🤖\n\nНапиши мне любой вопрос."
    )

@bot.message_handler(func=lambda message: True)
def answer(message):
    bot.reply_to(
        message,
        f"Я получил твой вопрос:\n{message.text}\n\n🤖 Скоро я научусь отвечать с помощью ИИ!"
    )

print("Bot started", flush=True)

try:
    bot.infinity_polling(skip_pending=True)
except Exception as e:
    print("BOT ERROR:", repr(e), flush=True)
    raise
# Railway deploy
