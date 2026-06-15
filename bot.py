import asyncio
import os
import logging
from flask import Flask, request, render_template_string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
import aiohttp
import time

# -------------------- Настройки --------------------
logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise RuntimeError("Переменная окружения TOKEN не установлена")

# Flask-приложение (веб-сайт + вебхук)
app = Flask(__name__)

# -------------------- База сайтов для поиска (реальный пробив) --------------------
SITES = {
    "Facebook": "https://www.facebook.com/{}",
    "Instagram": "https://www.instagram.com/{}",
    "Twitter": "https://twitter.com/{}",
    "YouTube": "https://www.youtube.com/@{}",
    "GitHub": "https://github.com/{}",
    "Reddit": "https://www.reddit.com/user/{}",
    "Pinterest": "https://www.pinterest.com/{}",
    "TikTok": "https://www.tiktok.com/@{}",
    "Snapchat": "https://www.snapchat.com/add/{}",
    "Telegram": "https://t.me/{}",
    "Steam": "https://steamcommunity.com/id/{}",
    "VK": "https://vk.com/{}",
    "Tumblr": "https://{}.tumblr.com",
    "Flickr": "https://www.flickr.com/photos/{}",
    "SoundCloud": "https://soundcloud.com/{}",
    "Medium": "https://medium.com/@{}",
    "Patreon": "https://www.patreon.com/{}",
    "Twitch": "https://www.twitch.tv/{}",
    "DeviantArt": "https://www.deviantart.com/{}",
    "About.me": "https://about.me/{}",
    "Spotify": "https://open.spotify.com/user/{}",
    "Keybase": "https://keybase.io/{}",
    "Bitbucket": "https://bitbucket.org/{}",
    "HackerNews": "https://news.ycombinator.com/user?id={}",
    "Pastebin": "https://pastebin.com/u/{}",
    "Roblox": "https://www.roblox.com/user.aspx?username={}",
    "BuzzFeed": "https://www.buzzfeed.com/{}",
    "Mixcloud": "https://www.mixcloud.com/{}",
    "WordPress": "https://{}.wordpress.com",
    "Blogger": "https://{}.blogspot.com",
    "LiveJournal": "https://{}.livejournal.com",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# -------------------- Асинхронная проверка профиля --------------------
async def check_site(session, name, url_template):
    url = url_template.format(name)
    try:
        async with session.get(url, headers=HEADERS, timeout=10, allow_redirects=True) as resp:
            if resp.status == 200:
                text = await resp.text()
                lower = text.lower()
                # Исключаем страницы-заглушки
                if any(phrase in lower for phrase in ["not found", "doesn't exist", "page not found", "sorry", "no user", "error 404"]):
                    return None
                return url
            return None
    except Exception as e:
        logging.debug(f"Ошибка проверки {url}: {e}")
        return None

async def osint_search(username: str) -> dict:
    found = {}
    async with aiohttp.ClientSession() as session:
        tasks = []
        site_names = []
        for site_name, url_template in SITES.items():
            site_names.append(site_name)
            tasks.append(check_site(session, username, url_template))
        results = await asyncio.gather(*tasks)
        for site, result in zip(site_names, results):
            if result:
                found[site] = result
    return found

# -------------------- Обработчики Telegram --------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📖 Помощь", callback_data="help")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        "🕵️ <b>Factum OSINT</b> — разведка по нику\n\n"
        "Я проверяю существование аккаунта на десятках платформ.\n"
        "Отправь команду: <code>/find username</code>\n"
        "Например: <code>/find ivanov</code>\n\n"
        "⚡ Найденные профили получаешь с прямыми ссылками."
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🔎 <b>Использование:</b>\n"
        "<code>/find никнейм</code> — поиск по 30+ сайтам.\n\n"
        "Результат реальный, не имитация.\n"
        "Бот написан в рамках OSINT-инструментария.",
        parse_mode=ParseMode.HTML
    )

async def find_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Укажи никнейм. Пример: <code>/find ivanov</code>", parse_mode=ParseMode.HTML)
        return
    username = context.args[0].strip()
    if len(username) < 2:
        await update.message.reply_text("❌ Слишком короткий никнейм.")
        return

    msg = await update.message.reply_text(f"🔎 <b>Ищу профили {username}...</b>", parse_mode=ParseMode.HTML)

    start_time = time.time()
    found = await osint_search(username)
    elapsed = round(time.time() - start_time, 1)

    if found:
        lines = [f"✅ <a href='{url}'>{site}</a>" for site, url in found.items()]
        result_text = (
            f"<b>🔍 Результаты для <code>{username}</code></b>\n"
            f"⏱️ Проверено за {elapsed} сек.\n\n"
            + "\n".join(lines)
        )
    else:
        result_text = f"<b>🔍 Для <code>{username}</code> ничего не найдено</b>\n⏱️ Проверено за {elapsed} сек."

    await msg.edit_text(result_text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

# -------------------- Веб-интерфейс (Flask) --------------------
def get_webpage_html():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Factum OSINT Bot</title>
    <style>
        body {
            margin: 0;
            background: #0a0f0f;
            font-family: 'Courier New', monospace;
            color: #0f0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            overflow: hidden;
        }
        .container {
            text-align: center;
            padding: 30px;
            border: 1px solid #0f0;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            background: rgba(0,20,0,0.6);
            box-shadow: 0 0 25px #0f0;
            animation: glow 2s infinite alternate;
        }
        h1 {
            font-size: 3em;
            text-shadow: 0 0 10px #0f0;
            margin: 0 0 20px;
        }
        .blink {
            animation: blink 1s steps(1) infinite;
        }
        @keyframes blink {
            50% { opacity: 0; }
        }
        @keyframes glow {
            from { box-shadow: 0 0 15px #0f0; }
            to { box-shadow: 0 0 35px #0f0, 0 0 80px #0f0; }
        }
        p {
            font-size: 1.2em;
            text-shadow: 0 0 5px #0f0;
        }
        .btn {
            display: inline-block;
            margin-top: 25px;
            padding: 10px 25px;
            border: 2px solid #0f0;
            color: #0f0;
            text-decoration: none;
            font-weight: bold;
            border-radius: 5px;
            transition: 0.3s;
        }
        .btn:hover {
            background: #0f0;
            color: #000;
            box-shadow: 0 0 20px #0f0;
        }
        .footer {
            margin-top: 30px;
            font-size: 0.8em;
            opacity: 0.7;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🕵️ FACTUM OSINT</h1>
        <p>Бот для поиска профилей по нику в реальном времени</p>
        <p class="blink">_</p>
        <a class="btn" href="https://t.me/YOUR_BOT_USERNAME" target="_blank">Перейти в бот</a>
        <div class="footer">
            © 2025 Factum Project
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(get_webpage_html())

# -------------------- Вебхук --------------------
async def telegram_webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return 'ok'

@app.route(f'/{TOKEN}', methods=['POST'])
async def webhook():
    return await telegram_webhook()

@app.route('/set_webhook')
async def set_webhook_route():
    url = request.url_root + TOKEN
    await application.bot.set_webhook(url)
    return f"Вебхук установлен на {url}"

# -------------------- Инициализация приложения Telegram --------------------
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("find", find_command))
application.add_handler(CommandHandler("help", lambda u,c: start(u,c)))  # /help = /start
application.add_handler(CallbackQueryHandler(help_callback, pattern="help"))

# -------------------- Запуск сервера --------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
