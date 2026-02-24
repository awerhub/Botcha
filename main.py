import telebot
import os
import random
import requests
from datetime import datetime

# ================== НАСТРОЙКИ ==================

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # например: -1001234567890

bot = telebot.TeleBot(TOKEN)

GAMES = [
    "evade",
    "mm2",
    "blox fruits",
    "doors",
    "arsenal"
]

# ================== ПОИСК СКРИПТА ==================

def find_script(game: str) -> str | None:
    query = f'{game} loadstring game:HttpGet'
    url = "https://api.github.com/search/code"

    params = {
        "q": query,
        "per_page": 5
    }

    headers = {
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        if r.status_code != 200:
            return None

        data = r.json()

        for item in data.get("items", []):
            raw_url = item["html_url"]
            raw_url = raw_url.replace(
                "https://github.com/",
                "https://raw.githubusercontent.com/"
            ).replace("/blob/", "/")

            check = requests.get(raw_url, timeout=10)
            if check.status_code == 200 and "loadstring(game:HttpGet" in check.text:
                return raw_url

    except Exception:
        return None

    return None

# ================== ОФОРМЛЕНИЕ ПОСТА ==================

def build_post(game: str) -> str:
    script_url = find_script(game)

    if not script_url:
        return f"❌ Не удалось найти рабочий скрипт для *{game}*"

    return (
        f"🎮 *{game.capitalize()}*\n\n"
        "🔥 Найден рабочий скрипт\n\n"
        "```lua\n"
        f'loadstring(game:HttpGet("{script_url}"))()\n'
        "```\n\n"
        f"🕒 Обновлено: {datetime.now().strftime('%d.%m.%Y')}"
    )

# ================== КОМАНДЫ ==================

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "Приветствую! 👋\n"
        "Я бот для оформления постов со скриптами.\n\n"
        "Список команд:\n\n"
        "/post <игра> — отправит уже оформленный пост (для проверки)\n"
        "/random — отправит оформленный пост со случайной игрой\n"
        "/postc <игра> — отправит пост сразу в канал"
    )

@bot.message_handler(commands=["post"])
def post_preview(message):
    game = message.text.replace("/post", "").strip()
    if not game:
        bot.send_message(message.chat.id, "❌ Укажи игру")
        return

    post = build_post(game)
    bot.send_message(message.chat.id, post, parse_mode="Markdown")

@bot.message_handler(commands=["postc"])
def post_channel(message):
    game = message.text.replace("/postc", "").strip()
    if not game:
        bot.send_message(message.chat.id, "❌ Укажи игру")
        return

    post = build_post(game)

    if post.startswith("❌"):
        bot.send_message(message.chat.id, post, parse_mode="Markdown")
        return

    bot.send_message(CHANNEL_ID, post, parse_mode="Markdown")
    bot.send_message(message.chat.id, "✅ Пост отправлен в канал")

@bot.message_handler(commands=["random"])
def random_post(message):
    game = random.choice(GAMES)
    post = build_post(game)
    bot.send_message(message.chat.id, post, parse_mode="Markdown")

# ================== ЗАПУСК ==================

print("Bot started")
bot.infinity_polling()
