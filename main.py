import telebot
import json
import random
import os

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = telebot.TeleBot(TOKEN)


def load_scripts():
    with open("scripts.json", "r", encoding="utf-8") as f:
        return json.load(f)

scripts = load_scripts()


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "Приветствую! Список команд:\n\n"
        "/post <игра> — отправит оформленный пост\n"
        "/postc <игра> — отправит пост в канал\n"
        "/random — случайный пост\n"
        "/search <слово> — поиск скриптов"
    )


# 🔍 ПОИСК
@bot.message_handler(commands=["search"])
def search(message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "Напиши слово для поиска")
        return

    query = args[1].lower()
    results = []

    for game in scripts.keys():
        if query in game.lower():
            results.append(game)

    if not results:
        bot.reply_to(message, "Ничего не найдено ❌")
        return

    text = "🔍 Найдено:\n\n"
    for g in results:
        text += f"• {g}\n"

    bot.send_message(message.chat.id, text)


# 📄 ПОСТ
@bot.message_handler(commands=["post"])
def post(message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "Напиши название игры")
        return

    game = args[1].lower()

    if game not in scripts:
        bot.reply_to(message, "Игра не найдена. Используй /search")
        return

    bot.send_message(message.chat.id, scripts[game])


# 📢 ПОСТ В КАНАЛ
@bot.message_handler(commands=["postc"])
def post_channel(message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "Напиши название игры")
        return

    game = args[1].lower()

    if game not in scripts:
        bot.reply_to(message, "Игра не найдена")
        return

    bot.send_message(CHANNEL_ID, scripts[game])
    bot.reply_to(message, "Отправлено в канал ✅")


# 🎲 РАНДОМ
@bot.message_handler(commands=["random"])
def random_post(message):
    game = random.choice(list(scripts.keys()))
    bot.send_message(message.chat.id, scripts[game])


bot.infinity_polling()
