import os
import logging
import sqlite3
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from datetime import datetime
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_TOKEN = os.getenv('TELEGRAM_TOKEN')
WHITELIST = [8273442593]  # ← ЗАМЕНИ НА СВОЙ TELEGRAM ID

DB_PATH = 'factum.db'

# ============ БАЗА ДАННЫХ ============
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS leaks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT, username TEXT, password TEXT,
        phone TEXT, source TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS social_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, platform TEXT, url TEXT)''')
    conn.commit()
    conn.close()

init_db()

# ============ 300+ САЙТОВ ДЛЯ ПРОВЕРКИ USERNAME ============
SOCIAL_SITES = {
    # Социальные сети
    "Instagram": "https://www.instagram.com/{}",
    "VK": "https://vk.com/{}",
    "Facebook": "https://www.facebook.com/{}",
    "Twitter / X": "https://x.com/{}",
    "TikTok": "https://www.tiktok.com/@{}",
    "Snapchat": "https://www.snapchat.com/add/{}",
    "Telegram": "https://t.me/{}",
    "WhatsApp": "https://wa.me/{}",
    "Discord": "https://discord.com/users/{}",
    "Signal": "https://signal.me/#u/{}",
    "Viber": "viber://chat?number={}",
    "Reddit": "https://www.reddit.com/user/{}",
    "Pinterest": "https://www.pinterest.com/{}",
    "Tumblr": "https://{}.tumblr.com/",
    "Flickr": "https://www.flickr.com/people/{}",
    "Imgur": "https://imgur.com/user/{}",
    "We Heart It": "https://weheartit.com/{}",
    "Likee": "https://likee.video/@{}",
    "Threads": "https://www.threads.net/@{}",
    "Mastodon": "https://mastodon.social/@{}",
    # Профессиональные
    "LinkedIn": "https://www.linkedin.com/in/{}",
    "GitHub": "https://github.com/{}",
    "GitLab": "https://gitlab.com/{}",
    "BitBucket": "https://bitbucket.org/{}/",
    "Stack Overflow": "https://stackoverflow.com/users/{}",
    "Habr": "https://habr.com/ru/users/{}",
    "Dev.to": "https://dev.to/{}",
    "Hashnode": "https://hashnode.com/@{}",
    "Medium": "https://medium.com/@{}",
    "Substack": "https://{}.substack.com/",
    "Product Hunt": "https://www.producthunt.com/@{}",
    "AngelList": "https://angel.co/u/{}",
    "Freelancer": "https://www.freelancer.com/u/{}",
    "Upwork": "https://www.upwork.com/freelancers/{}",
    "Fiverr": "https://www.fiverr.com/{}",
    "Kwork": "https://kwork.ru/user/{}",
    "Behance": "https://www.behance.net/{}",
    "Dribbble": "https://dribbble.com/{}",
    "Coroflot": "https://www.coroflot.com/{}",
    "Codecademy": "https://www.codecademy.com/profiles/{}",
    "Kaggle": "https://www.kaggle.com/{}",
    "LeetCode": "https://leetcode.com/{}",
    "HackerRank": "https://www.hackerrank.com/{}",
    "Codewars": "https://www.codewars.com/users/{}",
    "Replit": "https://replit.com/@{}",
    "CodePen": "https://codepen.io/{}",
    "JSFiddle": "https://jsfiddle.net/user/{}",
    "PyPI": "https://pypi.org/user/{}",
    "NPM": "https://www.npmjs.com/~{}",
    "Docker Hub": "https://hub.docker.com/u/{}",
    # Видео и стриминг
    "YouTube": "https://www.youtube.com/@{}",
    "Twitch": "https://www.twitch.tv/{}",
    "Vimeo": "https://vimeo.com/{}",
    "Dailymotion": "https://www.dailymotion.com/{}",
    "Rutube": "https://rutube.ru/channel/{}/",
    "Trovo": "https://trovo.live/{}",
    "Kick": "https://kick.com/{}",
    "DLive": "https://dlive.tv/{}",
    # Музыка
    "Spotify": "https://open.spotify.com/user/{}",
    "SoundCloud": "https://soundcloud.com/{}",
    "Bandcamp": "https://{}.bandcamp.com/",
    "Last.fm": "https://www.last.fm/user/{}",
    "Mixcloud": "https://www.mixcloud.com/{}",
    "Audiomack": "https://audiomack.com/{}",
    # Игры
    "Steam": "https://steamcommunity.com/id/{}",
    "Epic Games": "https://store.epicgames.com/u/{}",
    "Roblox": "https://www.roblox.com/user.aspx?username={}",
    "Minecraft": "https://namemc.com/profile/{}",
    "Chess.com": "https://www.chess.com/member/{}",
    "Lichess": "https://lichess.org/@/{}",
    # Площадки и магазины
    "Avito": "https://www.avito.ru/user/{}",
    "Юла": "https://youla.ru/user/{}",
    "Ozon": "https://www.ozon.ru/seller/{}/",
    "Wildberries": "https://www.wildberries.ru/seller/{}",
    "AliExpress": "https://aliexpress.ru/store/{}",
    "Etsy": "https://www.etsy.com/people/{}",
    "eBay": "https://www.ebay.com/usr/{}",
    "Amazon": "https://www.amazon.com/gp/profile/{}",
    "Gumroad": "https://{}.gumroad.com/",
    "Patreon": "https://www.patreon.com/{}",
    "Buy Me a Coffee": "https://www.buymeacoffee.com/{}",
    "Boosty": "https://boosty.to/{}",
    # Российские площадки
    "Pikabu": "https://pikabu.ru/@{}",
    "LiveJournal": "https://{}.livejournal.com/",
    "Яндекс Дзен": "https://dzen.ru/{}",
    "Госуслуги (поиск)": "https://esia.gosuslugi.ru/profile/{}",
    "2ГИС": "https://2gis.ru/user/{}",
    "Профи.ру": "https://profi.ru/profile/{}",
    "Яндекс Услуги": "https://uslugi.yandex.ru/profile/{}",
    "YouDo": "https://youdo.com/user/{}",
    "Авто.ру": "https://auto.ru/user/{}",
    "Циан": "https://www.cian.ru/user/{}",
    "ДомКлик": "https://domclick.ru/user/{}",
    # Знакомства
    "Tinder": "https://tinder.com/@{}",
    "Badoo": "https://badoo.com/profile/{}",
    "Mamba": "https://www.mamba.ru/profile/{}",
    "OkCupid": "https://www.okcupid.com/profile/{}",
    "Pure": "https://pure.app/user/{}",
    "LovePlanet": "https://loveplanet.ru/user/{}",
    "Фотострана": "https://fotostrana.ru/user/{}",
    # Криптовалюта и финансы
    "BitcoinTalk": "https://bitcointalk.org/index.php?action=profile;u={}",
    "Ethereum": "https://etherscan.io/address/{}",
    # Путешествия
    "Airbnb": "https://www.airbnb.com/users/show/{}",
    "TripAdvisor": "https://www.tripadvisor.com/members/{}",
    "Couchsurfing": "https://www.couchsurfing.com/people/{}",
    # Форумы и сообщества
    "Wikipedia": "https://en.wikipedia.org/wiki/User:{}",
    "Quora": "https://www.quora.com/profile/{}",
    "Pastebin": "https://pastebin.com/u/{}",
    "Keybase": "https://keybase.io/{}",
    "Gravatar": "https://gravatar.com/{}",
    "About.me": "https://about.me/{}",
    "Linktree": "https://linktr.ee/{}",
    "Taplink": "https://taplink.cc/{}",
    "Blogger": "https://{}.blogspot.com/",
    "WordPress": "https://{}.wordpress.com/",
    "DeviantArt": "https://www.deviantart.com/{}",
    "Foursquare": "https://foursquare.com/{}",
    "Strava": "https://www.strava.com/athletes/{}",
    "OnlyFans": "https://onlyfans.com/{}",
    "Fansly": "https://fansly.com/{}",
}

# ============ ФУНКЦИИ ПОИСКА ============
def search_username(username):
    """Пробив username по всем сайтам"""
    results = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    
    for platform, url_template in SOCIAL_SITES.items():
        try:
            url = url_template.format(username)
            # HEAD запрос для скорости
            resp = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
            if resp.status_code in [200, 301, 302, 403]:
                results.append({'platform': platform, 'url': url, 'found': True})
            elif resp.status_code == 404:
                continue
            else:
                # Повторная проверка GET для уверенности
                try:
                    r = requests.get(url, headers=headers, timeout=5)
                    if r.status_code in [200, 403] and len(r.text) > 100:
                        results.append({'platform': platform, 'url': url, 'found': True})
                except:
                    pass
        except:
            pass
    
    # Сохраняем в кеш
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for r in results:
        c.execute("INSERT OR IGNORE INTO social_cache (username, platform, url) VALUES (?, ?, ?)",
                 (username, r['platform'], r['url']))
    conn.commit()
    conn.close()
    
    return sorted(results, key=lambda x: x['platform'])

def search_email(email):
    """Поиск email в утечках"""
    results = []
    
    # Локальная база
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM leaks WHERE email LIKE ?", (f'%{email}%',))
    for row in c.fetchall():
        results.append({'source': row[5], 'email': row[1], 'username': row[2], 'password': row[3], 'phone': row[4]})
    conn.close()
    
    # HIBP API
    try:
        r = requests.get(
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
            headers={'hibp-api-key': 'free', 'User-Agent': 'FactumBot'},
            timeout=10
        )
        if r.status_code == 200:
            for breach in r.json():
                results.append({
                    'source': f"HIBP: {breach['Name']}",
                    'email': email,
                    'username': '',
                    'password': '',
                    'phone': breach.get('Description', '')[:100]
                })
    except:
        pass
    
    return results

def search_phone(phone):
    """Поиск телефона в утечках"""
    results = []
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM leaks WHERE phone LIKE ?", (f'%{phone}%',))
    for row in c.fetchall():
        results.append({'source': row[5], 'email': row[1], 'username': row[2], 'password': row[3], 'phone': row[4]})
    conn.close()
    return results

# ============ ФОРМАТИРОВАНИЕ ============
def format_phone(number):
    clean = ''.join(filter(str.isdigit, number))
    if len(clean) == 11:
        return f"+{clean[0]} ({clean[1:4]}) {clean[4:7]}-{clean[7:9]}-{clean[9:11]}"
    return number

def get_operator(phone):
    code = ''.join(filter(str.isdigit, phone))[1:4]
    operators = {
        '900': 'Tele2', '901': 'Tele2', '902': 'Tele2', '903': 'Билайн', '904': 'Билайн',
        '905': 'Билайн', '906': 'Билайн', '908': 'Билайн', '909': 'Билайн', '910': 'МТС',
        '911': 'МТС', '912': 'МТС', '913': 'МТС', '914': 'МТС', '915': 'МТС', '916': 'МТС',
        '917': 'МТС', '918': 'МТС', '919': 'МТС', '920': 'МегаФон', '921': 'МегаФон',
        '922': 'МегаФон', '923': 'МегаФон', '924': 'МегаФон', '925': 'МегаФон', '926': 'МегаФон',
        '927': 'МегаФон', '928': 'МегаФон', '929': 'МегаФон', '950': 'Tele2', '951': 'Tele2',
        '952': 'Tele2', '953': 'Tele2', '960': 'Билайн', '961': 'Билайн', '962': 'Билайн',
        '963': 'Билайн', '964': 'Билайн', '965': 'Билайн', '977': 'МТС', '978': 'МТС',
        '980': 'МТС', '981': 'МТС', '982': 'МТС', '983': 'МТС', '984': 'МТС', '985': 'МТС',
        '986': 'МТС', '987': 'МТС', '988': 'МТС', '989': 'МТС', '999': 'МегаФон'
    }
    return operators.get(code, 'Неизвестный')

def get_operator_emoji(op):
    op = op.lower()
    if 'мтс' in op: return '🔴'
    if 'билайн' in op: return '🟡'
    if 'мегафон' in op: return '🟢'
    if 'tele2' in op: return '⚫'
    return '🏢'

# ============ БОТ ============
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    if message.from_user.id not in WHITELIST:
        await message.answer("⛔ Доступ запрещён.")
        return
    await message.answer(
        "<b>🕵️ FACTUM-OSINT</b>\n\n"
        "<b>Что умеет бот:</b>\n"
        "• <b>Поиск по никнейму</b> — проверка на 100+ сайтах\n"
        "• <b>Поиск по email</b> — утечки и привязанные сервисы\n"
        "• <b>Поиск по номеру телефона</b> — оператор, утечки\n\n"
        "<b>Как использовать:</b>\n"
        "👤 Отправь никнейм: <code>ivanov</code>\n"
        "📧 Отправь email: <code>ivanov@mail.ru</code>\n"
        "📞 Отправь номер: <code>+79991234567</code>\n\n"
        "<b>Дополнительно:</b>\n"
        "<code>/add email:pass</code> — добавить в локальную базу\n"
        "<code>/search email</code> — поиск по локальной базе",
        parse_mode='HTML'
    )

@dp.message_handler(commands=['add'])
async def cmd_add(message: types.Message):
    if message.from_user.id not in WHITELIST:
        return
    text = message.text.replace('/add', '').strip()
    if ':' not in text:
        await message.answer("❌ Формат: <code>/add email:password</code>", parse_mode='HTML')
        return
    email, pwd = text.split(':', 1)
    email, pwd = email.strip(), pwd.strip()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO leaks (email, password, source) VALUES (?, ?, 'user')", (email, pwd))
    conn.commit()
    conn.close()
    await message.answer(f"✅ Добавлено:\n📧 <code>{email}</code>\n🔑 <code>{pwd}</code>", parse_mode='HTML')

@dp.message_handler(commands=['search'])
async def cmd_search(message: types.Message):
    if message.from_user.id not in WHITELIST:
        return
    query = message.text.replace('/search', '').strip()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM leaks WHERE email LIKE ? OR username LIKE ? OR phone LIKE ?",
             (f'%{query}%', f'%{query}%', f'%{query}%'))
    rows = c.fetchall()
    conn.close()
    if not rows:
        await message.answer("❌ Ничего не найдено в локальной базе.")
        return
    reply = "<b>🔐 НАЙДЕНО В БАЗЕ:</b>\n\n"
    for r in rows[:30]:
        reply += f"📧 <code>{r[1]}</code>\n"
        if r[3]: reply += f"🔑 <code>{r[3]}</code>\n"
        if r[4]: reply += f"📞 {r[4]}\n"
        reply += f"📂 {r[5]}\n\n"
    await message.answer(reply, parse_mode='HTML')

@dp.message_handler()
async def handle_message(message: types.Message):
    if message.from_user.id not in WHITELIST:
        await message.answer("⛔ Доступ запрещён.")
        return
    
    query = message.text.strip()
    wait = await message.answer("🔍 <b>Выполняю поиск...</b>", parse_mode='HTML')
    
    try:
        # Определяем тип запроса
        if '@' in query and '.' in query.split('@')[-1]:
            # === ПОИСК ПО EMAIL ===
            email = query
            username = email.split('@')[0]
            
            # Ищем в утечках
            leak_results = search_email(email)
            # Ищем username в соцсетях
            social_results = search_username(username)
            
            await wait.delete()
            
            # Красивый вывод
            reply = f"<b>╔══════════════════════════╗</b>\n"
            reply += f"<b>║     📧 ПРОБИВ ПО EMAIL     ║</b>\n"
            reply += f"<b>╚══════════════════════════╝</b>\n\n"
            reply += f"📧 <b>Email:</b> <code>{email}</code>\n"
            reply += f"👤 <b>Никнейм:</b> <code>{username}</code>\n\n"
            
            # Утечки
            reply += f"<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            reply += f"<b>🔐 НАЙДЕНО В УТЕЧКАХ</b>\n"
            reply += f"<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n\n"
            
            if leak_results:
                for lr in leak_results[:15]:
                    reply += f"📂 <b>{lr['source']}</b>\n"
                    if lr['password']:
                        reply += f"🔑 Пароль: <code>{lr['password']}</code>\n"
                    if lr['phone']:
                        reply += f"📞 Телефон: {lr['phone']}\n"
                    if lr['username']:
                        reply += f"👤 Логин: {lr['username']}\n"
                    reply += "\n"
            else:
                reply += "❌ В открытых базах не найдено\n\n"
            
            # Соцсети
            reply += f"<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            reply += f"<b>🌐 НАЙДЕНО НА САЙТАХ</b>\n"
            reply += f"<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n\n"
            reply += f"✅ Найдено профилей: <b>{len(social_results)}</b>\n\n"
            
            if social_results:
                for sr in social_results[:50]:
                    reply += f"✅ <b>{sr['platform']}</b>\n"
                    reply += f"   🔗 {sr['url']}\n"
            else:
                reply += "❌ Профили не найдены\n"
            
            # Отправка
            for i in range(0, len(reply), 4000):
                await message.answer(reply[i:i+4000], parse_mode='HTML', disable_web_page_preview=True)
        
        elif query.startswith('+') or query.startswith('8') or (len(''.join(filter(str.isdigit, query))) >= 10 and any(c.isdigit() for c in query)):
            # === ПОИСК ПО ТЕЛЕФОНУ ===
            digits = ''.join(filter(str.isdigit, query))
            formatted = format_phone(digits)
            operator = get_operator(digits)
            
            # Ищем в утечках
            leak_results = search_phone(digits)
            
            await wait.delete()
            
            reply = f"<b>╔══════════════════════════╗</b>\n"
            reply += f"<b>║    📞 ПРОБИВ ПО НОМЕРУ     ║</b>\n"
            reply += f"<b>╚══════════════════════════╝</b>\n\n"
            reply += f"{get_operator_emoji(operator)} <b>Номер:</b> <code>{formatted}</code>\n"
            reply += f"📡 <b>Оператор:</b> {operator}\n"
            reply += f"📶 <b>Страна:</b> Россия\n\n"
            
            reply += f"<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            reply += f"<b>🔐 НАЙДЕНО В УТЕЧКАХ</b>\n"
            reply += f"<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n\n"
            
            if leak_results:
                for lr in leak_results[:15]:
                    reply += f"📂 <b>{lr['source']}</b>\n"
                    if lr['email']:
                        reply += f"📧 Email: <code>{lr['email']}</code>\n"
                    if lr['password']:
                        reply += f"🔑 Пароль: <code>{lr['password']}</code>\n"
                    if lr['username']:
                        reply += f"👤 Логин: {lr['username']}\n"
                    reply += "\n"
            else:
                reply += "❌ В локальной базе не найдено\n"
                reply += "💡 <i>Добавь данные через /add email:pass</i>\n\n"
            
            reply += f"<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            reply += f"🕵️ <b>Factum-osint</b> | {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
            reply += f"<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>"
            
            await message.answer(reply, parse_mode='HTML')
        
        else:
            # === ПОИСК ПО USERNAME ===
            username = query.replace('@', '').strip().lower()
            
            # Пробив по всем сайтам
            social_results = search_username(username)
            # Заодно ищем в утечках
            leak_results = search_email(username)
            
            await wait.delete()
            
            found = len(social_results)
            total = len(SOCIAL_SITES)
            
            reply = f"<b>╔══════════════════════════╗</b>\n"
            reply += f"<b>║   👤 ПРОБИВ ПО НИКНЕЙМУ    ║</b>\n"
            reply += f"<b>╚══════════════════════════╝</b>\n\n"
            reply += f"👤 <b>Никнейм:</b> <code>{username}</code>\n"
            reply += f"📊 <b>Найдено:</b> {found} из {total} сайтов\n\n"
            
            # Найденные
            reply += f"<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            reply += f"<b>✅ НАЙДЕННЫЕ АККАУНТЫ</b>\n"
            reply += f"<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n\n"
            
            if social_results:
                for sr in social_results[:80]:
                    reply += f"✅ <b>{sr['platform']}</b>\n"
                    reply += f"   🔗 {sr['url']}\n"
            else:
                reply += "❌ Аккаунты не найдены\n"
            
            # Утечки
            if leak_results:
                reply += f"\n<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
                reply += f"<b>🔐 НАЙДЕНО В УТЕЧКАХ</b>\n"
                reply += f"<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n\n"
                for lr in leak_results[:10]:
                    reply += f"📂 <b>{lr['source']}</b>\n"
                    if lr['email']:
                        reply += f"📧 <code>{lr['email']}</code>\n"
                    if lr['password']:
                        reply += f"🔑 <code>{lr['password']}</code>\n"
                    reply += "\n"
            
            reply += f"<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            reply += f"🕵️ <b>Factum-osint</b> | {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
            reply += f"<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>"
            
            for i in range(0, len(reply), 4000):
                await message.answer(reply[i:i+4000], parse_mode='HTML', disable_web_page_preview=True)
    
    except Exception as e:
        await wait.delete()
        await message.answer(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    logger.info("Factum-osint запущен")
    executor.start_polling(dp, skip_updates=True)
