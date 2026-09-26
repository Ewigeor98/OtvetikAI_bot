import os
import telebot
from groq import Groq

TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_API_KEY)


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "👋 Привет! Я «Ответик» 🤖\n\n"
        "Я помогу написать сообщение, поздравление, объявление, "
        "вежливый ответ или переформулировать текст.\n\n"
        "Просто напиши мне, что тебе нужно ✨"
    )


@bot.message_handler(func=lambda message: True)
def answer(message):
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты «Ответик» — дружелюбный русскоязычный AI-помощник. "
                        "Помогай пользователю писать сообщения, поздравления, "
                        "объявления, ответы и другие тексты. "
                        "Отвечай понятно, естественно и по существу."
                    )
                },
                {
                    "role": "user",
                    "content": message.text
                }
            ]
        )

        bot.reply_to(message, response.choices[0].message.content)

    except Exception as e:
        print("AI ERROR:", repr(e), flush=True)
        bot.reply_to(
            message,
            "😔 Не получилось получить ответ. Попробуй ещё раз чуть позже."
        )
print("Bot started", flush=True)
bot.infinity_polling(skip_pending=True)

