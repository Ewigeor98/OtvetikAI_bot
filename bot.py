import os
import sqlite3
import telebot
from groq import Groq

TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_API_KEY)
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    requests_used INTEGER DEFAULT 0
)
""")
conn.commit()
REE_LIMIT = 10
def get_requests_left(user_id): 
    cursor.execute( 
        "SELECT requests_used FROM users WHERE user_id = ?",
        (user_id,)
    ) 
    user = cursor.fetchone()
if user is None:
    cursor.execute(
        "INSERT INTO users (user_id, requests_used) VALUES (?, 0)",
        (user_id,)
    )
    conn.commit()
    return FREE_LIMIT

return max(0, FREE_LIMIT - user[0])
def use_request(user_id):
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, requests_used) VALUES (?, 0)",
        (user_id,)
    )
    cursor.execute(
        "UPDATE users SET requests_used = requests_used + 1 WHERE user_id = ?",
        (user_id,)
    )
    conn.commit()
menu = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
menu.row("💬 Ответить на сообщение", "❤️ Поздравление")
menu.row("✨ Перефразировать", "📝 Написать текст")

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "👋 Привет! Я «Ответик» 🤖\n\n"
        "Я помогу написать сообщение, поздравление, объявление, "
        "вежливый ответ или переформулировать текст.\n\n"
        "Просто напиши мне, что тебе нужно ✨",
        reply_markup=menu
    )

@bot.message_handler(func=lambda message: message.text == "❤️ Поздравление")
def congratulations(message):
    msg = bot.reply_to(
        message,
        "❤️ Кого будем поздравлять и с каким праздником?\n\n"
        "Например: маму с днём рождения"
    )
    bot.register_next_step_handler(msg, make_congratulation)


def make_congratulation(message):
    if get_requests_left(message.from_user.id) <= 0:
        bot.reply_to(
            message,
            "🔒 Бесплатные запросы закончились."
        )
        return
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты «Ответик». Напиши красивое, тёплое и естественное "
                        "поздравление на русском языке по просьбе пользователя. "
                        "Выдай только готовый текст поздравления."
                    )
                },
                {
                    "role": "user",
                    "content": message.text
                }
            ]
        )
        bot.reply_to(message, response.choices[0].message.content)
        use_request(message.from_user.id)
    except Exception as e:
        print("AI ERROR:", repr(e), flush=True)
        bot.reply_to(message, "😔 Не получилось создать поздравление. Попробуй ещё раз.")
@bot.message_handler(func=lambda message: message.text == "💬 Ответить на сообщение")
def reply_to_message(message):
    msg = bot.reply_to(
        message,
        "💬 Пришли мне сообщение, на которое нужно ответить.\n\n"
        "Я составлю готовый ответ ✨"
    )
    bot.register_next_step_handler(msg, make_reply)


def make_reply(message):
    if get_requests_left(message.from_user.id) <= 0:
        bot.reply_to(
            message,
            "🔒 Бесплатные запросы закончились."
        )
        return
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты «Ответик». Пользователь присылает сообщение, "
                        "на которое ему нужно ответить. Напиши вежливый, "
                        "естественный и подходящий по смыслу ответ на русском языке. "
                        "Выдай только готовый текст ответа."
                    )
                },
                {
                    "role": "user",
                    "content": message.text
                }
            ]
        )
        bot.reply_to(message, response.choices[0].message.content)
        use_request(message.from_user.id)
    except Exception as e:
        print("AI ERROR:", repr(e), flush=True)
        bot.reply_to(message, "😔 Не получилось составить ответ. Попробуй ещё раз.")
@bot.message_handler(func=lambda message: message.text == "✨ Перефразировать")
def rephrase_text(message):
    msg = bot.reply_to(
        message,
        "✨ Пришли текст, который нужно перефразировать.\n\n"
        "Я сделаю его красивее и естественнее."
    )
    bot.register_next_step_handler(msg, make_rephrase)


def make_rephrase(message):
    if get_requests_left(message.from_user.id) <= 0:
        bot.reply_to(
            message,
            "🔒 Бесплатные запросы закончились."
        )
        return
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты «Ответик». Перефразируй текст пользователя "
                        "на русском языке, сохранив его смысл. "
                        "Сделай текст грамотным, естественным и красивым. "
                        "Выдай только готовый вариант текста."
                    )
                },
                {
                    "role": "user",
                    "content": message.text
                }
            ]
        )
        bot.reply_to(message, response.choices[0].message.content)
        use_request(message.from_user.id)
    except Exception as e:
        print("AI ERROR:", repr(e), flush=True)
        bot.reply_to(message, "😔 Не получилось перефразировать текст. Попробуй ещё раз.")
@bot.message_handler(func=lambda message: message.text == "📝 Написать текст")
def write_text(message):
    msg = bot.reply_to(
        message,
        "📝 Расскажи, какой текст тебе нужно написать.\n\n"
        "Например: объявление о продаже машины или сообщение клиенту."
    )
    bot.register_next_step_handler(msg, make_text)


def make_text(message):
    if get_requests_left(message.from_user.id) <= 0:
       bot.reply_to(
           message,
           "🔒 Бесплатные запросы закончились."
       )
       return
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты «Ответик». Напиши готовый текст по просьбе пользователя "
                        "на русском языке. Текст должен быть грамотным, естественным "
                        "и подходить под ситуацию. Выдай только готовый текст."
                    )
                },
                {
                    "role": "user",
                    "content": message.text
                }
            ]
        )
        bot.reply_to(message, response.choices[0].message.content)
        use_request(message.from_user.id)
    except Exception as e:
        print("AI ERROR:", repr(e), flush=True)
        bot.reply_to(message, "😔 Не получилось написать текст. Попробуй ещё раз.")
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

