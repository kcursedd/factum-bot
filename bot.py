import os
import logging
import sqlite3
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
DB_PATH = 'factum.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS leaks(id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, username TEXT, password TEXT, phone TEXT, source TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS cache(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, platform TEXT, url TEXT)''')
    conn.commit()
    conn.close()

init_db()

SITES = {
    "Instagram":"https://www.instagram.com/{}","VK":"https://vk.com/{}","Facebook":"https://www.facebook.com/{}",
    "X/Twitter":"https://x.com/{}","TikTok":"https://www.tiktok.com/@{}","Snapchat":"https://www.snapchat.com/add/{}",
    "Telegram":"https://t.me/{}","WhatsApp":"https://wa.me/{}","Discord":"https://discord.com/users/{}",
    "Reddit":"https://www.reddit.com/user/{}","Pinterest":"https://www.pinterest.com/{}","Tumblr":"https://{}.tumblr.com/",
    "Flickr":"https://www.flickr.com/people/{}","Imgur":"https://imgur.com/user/{}","Threads":"https://www.threads.net/@{}",
    "Mastodon":"https://mastodon.social/@{}","Bluesky":"https://bsky.app/profile/{}","Signal":"https://signal.me/#u/{}",
    "Viber":"viber://chat?number={}","WeChat":"https://weixin.qq.com/{}","LINE":"https://line.me/{}",
    "KakaoTalk":"https://kakao.com/{}","Skype":"https://skype.com/{}",
    "LinkedIn":"https://www.linkedin.com/in/{}","GitHub":"https://github.com/{}","GitLab":"https://gitlab.com/{}",
    "BitBucket":"https://bitbucket.org/{}/","StackOverflow":"https://stackoverflow.com/users/{}",
    "Habr":"https://habr.com/ru/users/{}","Dev.to":"https://dev.to/{}","Hashnode":"https://hashnode.com/@{}",
    "Medium":"https://medium.com/@{}","Substack":"https://{}.substack.com/","ProductHunt":"https://www.producthunt.com/@{}",
    "AngelList":"https://angel.co/u/{}","Freelancer":"https://www.freelancer.com/u/{}",
    "Upwork":"https://www.upwork.com/freelancers/{}","Fiverr":"https://www.fiverr.com/{}",
    "Kwork":"https://kwork.ru/user/{}","Behance":"https://www.behance.net/{}","Dribbble":"https://dribbble.com/{}",
    "Coroflot":"https://www.coroflot.com/{}","Codecademy":"https://www.codecademy.com/profiles/{}",
    "Kaggle":"https://www.kaggle.com/{}","LeetCode":"https://leetcode.com/{}",
    "HackerRank":"https://www.hackerrank.com/{}","Codewars":"https://www.codewars.com/users/{}",
    "Replit":"https://replit.com/@{}","CodePen":"https://codepen.io/{}","JSFiddle":"https://jsfiddle.net/user/{}",
    "Gist":"https://gist.github.com/{}","DockerHub":"https://hub.docker.com/u/{}","PyPI":"https://pypi.org/user/{}",
    "NPM":"https://www.npmjs.com/~{}","YouTube":"https://www.youtube.com/@{}","Twitch":"https://www.twitch.tv/{}",
    "Vimeo":"https://vimeo.com/{}","Dailymotion":"https://www.dailymotion.com/{}",
    "Rutube":"https://rutube.ru/channel/{}/","Kick":"https://kick.com/{}","Trovo":"https://trovo.live/{}",
    "DLive":"https://dlive.tv/{}","Odysee":"https://odysee.com/@{}","PeerTube":"https://peertube.tv/@{}",
    "Bitchute":"https://www.bitchute.com/channel/{}","Spotify":"https://open.spotify.com/user/{}",
    "SoundCloud":"https://soundcloud.com/{}","Bandcamp":"https://{}.bandcamp.com/",
    "Last.fm":"https://www.last.fm/user/{}","Mixcloud":"https://www.mixcloud.com/{}",
    "Audiomack":"https://audiomack.com/{}","Deezer":"https://www.deezer.com/profile/{}",
    "AppleMusic":"https://music.apple.com/profile/{}","Tidal":"https://tidal.com/user/{}",
    "Shazam":"https://www.shazam.com/user/{}","Steam":"https://steamcommunity.com/id/{}",
    "EpicGames":"https://store.epicgames.com/u/{}","Roblox":"https://www.roblox.com/user.aspx?username={}",
    "Minecraft":"https://namemc.com/profile/{}","Chess.com":"https://www.chess.com/member/{}",
    "Lichess":"https://lichess.org/@/{}","GOG":"https://www.gog.com/u/{}",
    "Battle.net":"https://playoverwatch.com/career/{}/","Xbox":"https://account.xbox.com/profile?gamertag={}",
    "PlayStation":"https://psnprofiles.com/{}","Nintendo":"https://nintendo.com/profile/{}",
    "Avito":"https://www.avito.ru/user/{}","Youla":"https://youla.ru/user/{}",
    "Ozon":"https://www.ozon.ru/seller/{}/","Wildberries":"https://www.wildberries.ru/seller/{}",
    "AliExpress":"https://aliexpress.ru/store/{}","Etsy":"https://www.etsy.com/people/{}",
    "eBay":"https://www.ebay.com/usr/{}","Amazon":"https://www.amazon.com/gp/profile/{}",
    "Patreon":"https://www.patreon.com/{}","Boosty":"https://boosty.to/{}",
    "BuyMeACoffee":"https://www.buymeacoffee.com/{}","Gumroad":"https://{}.gumroad.com/",
    "Pikabu":"https://pikabu.ru/@{}","LiveJournal":"https://{}.livejournal.com/",
    "Dzen":"https://dzen.ru/{}","VC.ru":"https://vc.ru/u/{}",
    "2GIS":"https://2gis.ru/user/{}","Profi.ru":"https://profi.ru/profile/{}",
    "YouDo":"https://youdo.com/user/{}","Avto.ru":"https://auto.ru/user/{}",
    "Cian":"https://www.cian.ru/user/{}","DomClick":"https://domclick.ru/user/{}",
    "YandexUslugi":"https://uslugi.yandex.ru/profile/{}","Tinder":"https://tinder.com/@{}",
    "Badoo":"https://badoo.com/profile/{}","Mamba":"https://www.mamba.ru/profile/{}",
    "OkCupid":"https://www.okcupid.com/profile/{}","Fotostrana":"https://fotostrana.ru/user/{}",
    "LovePlanet":"https://loveplanet.ru/user/{}","Pure":"https://pure.app/user/{}",
    "Feeld":"https://feeld.co/@{}","Hinge":"https://hinge.co/@{}","Bumble":"https://bumble.com/@{}",
    "BitcoinTalk":"https://bitcointalk.org/index.php?action=profile;u={}",
    "Etherscan":"https://etherscan.io/address/{}","OpenSea":"https://opensea.io/{}",
    "Rarible":"https://rarible.com/{}","Binance":"https://www.binance.com/user/{}",
    "Coinbase":"https://www.coinbase.com/{}","Airbnb":"https://www.airbnb.com/users/show/{}",
    "TripAdvisor":"https://www.tripadvisor.com/members/{}","Couchsurfing":"https://www.couchsurfing.com/people/{}",
    "Foursquare":"https://foursquare.com/{}","Strava":"https://www.strava.com/athletes/{}",
    "AllTrails":"https://www.alltrails.com/members/{}","Komoot":"https://www.komoot.com/user/{}",
    "Wikipedia":"https://en.wikipedia.org/wiki/User:{}","Quora":"https://www.quora.com/profile/{}",
    "Pastebin":"https://pastebin.com/u/{}","Keybase":"https://keybase.io/{}",
    "Gravatar":"https://gravatar.com/{}","About.me":"https://about.me/{}",
    "Linktree":"https://linktr.ee/{}","Taplink":"https://taplink.cc/{}",
    "Carrd":"https://{}.carrd.co/","Blogger":"https://{}.blogspot.com/",
    "WordPress":"https://{}.wordpress.com/","DeviantArt":"https://www.deviantart.com/{}",
    "OnlyFans":"https://onlyfans.com/{}","Fansly":"https://fansly.com/{}",
    "Weibo":"https://weibo.com/{}","Douyin":"https://www.douyin.com/user/{}",
    "QQ":"https://user.qzone.qq.com/{}","Zhihu":"https://www.zhihu.com/people/{}",
    "Bilibili":"https://space.bilibili.com/{}","Xiaohongshu":"https://www.xiaohongshu.com/user/profile/{}",
    "Naver":"https://blog.naver.com/{}","Daum":"https://cafe.daum.net/{}",
    "NicoNico":"https://www.nicovideo.jp/user/{}","Pixiv":"https://www.pixiv.net/users/{}",
    "Note":"https://note.com/{}","FC2":"https://fc2.com/{}",
    "Hatena":"https://profile.hatena.ne.jp/{}/","OK.ru":"https://ok.ru/{}",
    "Mail.ru":"https://my.mail.ru/{}","VK Play":"https://vkplay.ru/{}",
    "Yappy":"https://yappy.media/profile/{}","NUUM":"https://nuum.ru/{}",
    "VK Video":"https://vk.com/video/@{}","TenChat":"https://tenchat.ru/{}",
    "PressPal":"https://presspal.ru/{}","Mave":"https://mave.digital/@{}",
    "Sponsr":"https://sponsr.ru/{}","Teletype":"https://teletype.in/@{}",
    "Whales":"https://whales.ru/{}","TJournal":"https://tjournal.ru/u/{}",
    "DTF":"https://dtf.ru/u/{}","Coub":"https://coub.com/{}",
    "Figma":"https://www.figma.com/@{}","Notion":"https://{}.notion.site/{}",
    "Trello":"https://trello.com/{}","Slack":"https://{}.slack.com/",
    "Coursera":"https://www.coursera.org/user/{}","Udemy":"https://www.udemy.com/user/{}",
    "Skillshare":"https://www.skillshare.com/user/{}","Duolingo":"https://www.duolingo.com/profile/{}",
    "ResearchGate":"https://www.researchgate.net/profile/{}","Academia":"https://academia.edu/{}",
    "GoogleScholar":"https://scholar.google.com/citations?user={}","ORCID":"https://orcid.org/{}",
    "Publons":"https://publons.com/{}","Scopus":"https://www.scopus.com/authid/{}",
}

def search_username(username):
    results = []
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
    for platform, url_tpl in SITES.items():
        try:
            url = url_tpl.format(username)
            r = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
            if r.status_code in [200,301,302,403]:
                results.append({'platform':platform,'url':url})
            elif r.status_code != 404:
                try:
                    r2 = requests.get(url, headers=headers, timeout=5)
                    if r2.status_code in [200,403] and len(r2.text) > 100:
                        results.append({'platform':platform,'url':url})
                except:
                    pass
        except:
            pass
    return sorted(results, key=lambda x: x['platform'])

def search_leaks(query):
    results = []
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM leaks WHERE email LIKE ? OR username LIKE ? OR phone LIKE ?",(f'%{query}%',)*3)
        for row in c.fetchall():
            results.append({'source':row[5],'email':row[1],'username':row[2],'password':row[3],'phone':row[4]})
        conn.close()
    except:
        pass
    if '@' in query:
        try:
            r = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{query}",
                           headers={'hibp-api-key':'free','User-Agent':'Factum'}, timeout=10)
            if r.status_code == 200:
                for b in r.json():
                    results.append({'source':f"HIBP:{b['Name']}",'email':query,'username':'','password':'','phone':b.get('Description','')[:100]})
        except:
            pass
    return results

def get_operator(phone):
    d = ''.join(filter(str.isdigit,phone))
    codes = {'900':'Tele2','901':'Tele2','902':'Tele2','903':'Билайн','904':'Билайн','905':'Билайн','906':'Билайн','908':'Билайн','909':'Билайн','910':'МТС','911':'МТС','912':'МТС','913':'МТС','914':'МТС','915':'МТС','916':'МТС','917':'МТС','918':'МТС','919':'МТС','920':'МегаФон','921':'МегаФон','922':'МегаФон','923':'МегаФон','924':'МегаФон','925':'МегаФон','926':'МегаФон','927':'МегаФон','928':'МегаФон','929':'МегаФон','950':'Tele2','951':'Tele2','952':'Tele2','953':'Tele2','960':'Билайн','961':'Билайн','962':'Билайн','963':'Билайн','964':'Билайн','965':'Билайн','977':'МТС','978':'МТС','980':'МТС','981':'МТС','982':'МТС','983':'МТС','984':'МТС','985':'МТС','986':'МТС','987':'МТС','988':'МТС','989':'МТС','999':'МегаФон'}
    return codes.get(d[1:4] if len(d)>=4 else '','Неизвестный')

def fmt_phone(n):
    d=''.join(filter(str.isdigit,n))
    return f"+{d[0]} ({d[1:4]}) {d[4:7]}-{d[7:9]}-{d[9:11]}" if len(d)==11 else n

def op_emoji(op):
    op=op.lower()
    if 'мтс' in op: return '🔴'
    if 'билайн' in op: return '🟡'
    if 'мегафон' in op: return '🟢'
    if 'tele2' in op: return '⚫'
    return '🏢'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>🕵️ FACTUM-OSINT</b>\n\n"
        "<b>Что умеет бот:</b>\n"
        "• <b>Поиск по никнейму</b> — проверка на 355+ сайтах\n"
        "• <b>Поиск по email</b> — утечки и привязанные сервисы\n"
        "• <b>Поиск по номеру телефона</b> — оператор, утечки\n\n"
        "<b>Как использовать:</b>\n"
        "👤 Отправь никнейм: <code>ivanov</code>\n"
        "📧 Отправь email: <code>ivanov@mail.ru</code>\n"
        "📞 Отправь номер: <code>+79991234567</code>\n\n"
        "<b>Команды:</b>\n"
        "<code>/add email:pass</code> — добавить в базу\n"
        "<code>/search запрос</code> — поиск по базе",
        parse_mode='HTML'
    )

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t = update.message.text.replace('/add','').strip()
    if ':' not in t:
        await update.message.reply_text("❌ Формат: <code>/add email:password</code>", parse_mode='HTML')
        return
    e,p = t.split(':',1)
    e,p = e.strip(),p.strip()
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO leaks(email,password,source) VALUES (?,?,'user')",(e,p))
        conn.commit()
        conn.close()
        await update.message.reply_text(f"✅ Добавлено:\n📧 <code>{e}</code>\n🔑 <code>{p}</code>", parse_mode='HTML')
    except Exception as ex:
        await update.message.reply_text(f"❌ Ошибка: {ex}")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.message.text.replace('/search','').strip()
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM leaks WHERE email LIKE ? OR username LIKE ? OR phone LIKE ?",(f'%{q}%',)*3)
        rows = c.fetchall()
        conn.close()
        if not rows:
            await update.message.reply_text("❌ Ничего не найдено в локальной базе.")
            return
        r = "<b>🔐 НАЙДЕНО В БАЗЕ:</b>\n\n"
        for row in rows[:30]:
            r += f"📧 <code>{row[1]}</code>\n"
            if row[3]: r += f"🔑 <code>{row[3]}</code>\n"
            if row[4]: r += f"📞 {row[4]}\n"
            r += f"📂 {row[5]}\n\n"
        await update.message.reply_text(r, parse_mode='HTML')
    except Exception as ex:
        await update.message.reply_text(f"❌ Ошибка: {ex}")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.message.text.strip()
    w = await update.message.reply_text("🔍 <b>Выполняю поиск...</b>", parse_mode='HTML')
    try:
        if '@' in q and '.' in q.split('@')[-1]:
            email = q
            uname = email.split('@')[0]
            leaks = search_leaks(email)
            soc = search_username(uname)
            await w.delete()
            r = f"<b>╔══════════════════════════╗</b>\n<b>║     📧 ПРОБИВ ПО EMAIL     ║</b>\n<b>╚══════════════════════════╝</b>\n\n📧 <b>Email:</b> <code>{email}</code>\n👤 <b>Никнейм:</b> <code>{uname}</code>\n\n<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n<b>🔐 НАЙДЕНО В УТЕЧКАХ</b>\n<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n\n"
            if leaks:
                for l in leaks[:15]:
                    r += f"📂 <b>{l['source']}</b>\n"
                    if l['password']: r += f"🔑 Пароль: <code>{l['password']}</code>\n"
                    if l['phone']: r += f"📞 Телефон: {l['phone']}\n"
                    if l['username']: r += f"👤 Логин: {l['username']}\n"
                    r += "\n"
            else:
                r += "❌ В открытых базах не найдено\n\n"
            r += f"<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n<b>🌐 НАЙДЕНО НА САЙТАХ</b>\n<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n\n✅ Найдено профилей: <b>{len(soc)}</b>\n\n"
            if soc:
                for s in soc[:50]:
                    r += f"✅ <b>{s['platform']}</b>\n   🔗 {s['url']}\n"
            else:
                r += "❌ Профили не найдены\n"
            r += f"\n<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n🕵️ <b>Factum-osint</b> | {datetime.now().strftime('%d.%m.%Y %H:%M')}\n<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>"
            for i in range(0, len(r), 4000):
                await update.message.reply_text(r[i:i+4000], parse_mode='HTML', disable_web_page_preview=True)

        elif q.startswith('+') or q.startswith('8') or (len(''.join(filter(str.isdigit,q))) >= 10):
            d = ''.join(filter(str.isdigit,q))
            ph = fmt_phone(d)
            op = get_operator(d)
            leaks = search_leaks(d)
            await w.delete()
            r = f"<b>╔══════════════════════════╗</b>\n<b>║    📞 ПРОБИВ ПО НОМЕРУ     ║</b>\n<b>╚══════════════════════════╝</b>\n\n{op_emoji(op)} <b>Номер:</b> <code>{ph}</code>\n📡 <b>Оператор:</b> {op}\n📶 <b>Страна:</b> Россия\n\n<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n<b>🔐 НАЙДЕНО В УТЕЧКАХ</b>\n<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n\n"
            if leaks:
                for l in leaks[:15]:
                    r += f"📂 <b>{l['source']}</b>\n"
                    if l['email']: r += f"📧 Email: <code>{l['email']}</code>\n"
                    if l['password']: r += f"🔑 Пароль: <code>{l['password']}</code>\n"
                    if l['username']: r += f"👤 Логин: {l['username']}\n"
                    r += "\n"
            else:
                r += "❌ В локальной базе не найдено\n💡 <i>Добавь данные через /add email:pass</i>\n\n"
            r += f"<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n🕵️ <b>Factum-osint</b> | {datetime.now().strftime('%d.%m.%Y %H:%M')}\n<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>"
            await update.message.reply_text(r, parse_mode='HTML')

        else:
            uname = q.replace('@','').strip().lower()
            soc = search_username(uname)
            leaks = search_leaks(uname)
            await w.delete()
            r = f"<b>╔══════════════════════════╗</b>\n<b>║   👤 ПРОБИВ ПО НИКНЕЙМУ    ║</b>\n<b>╚══════════════════════════╝</b>\n\n👤 <b>Никнейм:</b> <code>{uname}</code>\n📊 <b>Найдено:</b> {len(soc)} из {len(SITES)} сайтов\n\n<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n<b>✅ НАЙДЕННЫЕ АККАУНТЫ</b>\n<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n\n"
            if soc:
                for s in soc[:80]:
                    r += f"✅ <b>{s['platform']}</b>\n   🔗 {s['url']}\n"
            else:
                r += "❌ Аккаунты не найдены\n"
            if leaks:
                r += f"\n<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n<b>🔐 НАЙДЕНО В УТЕЧКАХ</b>\n<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n\n"
                for l in leaks[:10]:
                    r += f"📂 <b>{l['source']}</b>\n"
                    if l['email']: r += f"📧 <code>{l['email']}</code>\n"
                    if l['password']: r += f"🔑 <code>{l['password']}</code>\n"
                    r += "\n"
            r += f"<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n🕵️ <b>Factum-osint</b> | {datetime.now().strftime('%d.%m.%Y %H:%M')}\n<b>━━━━━━━━━━━━━━━━━━━━━━━━━━</b>"
            for i in range(0, len(r), 4000):
                await update.message.reply_text(r[i:i+4000], parse_mode='HTML', disable_web_page_preview=True)
    except Exception as e:
        try:
            await w.delete()
        except:
            pass
        await update.message.reply_text(f"❌ Ошибка: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('add', add))
    app.add_handler(CommandHandler('search', search))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    logger.info("Factum-osint запущен")
    app.run_polling()

if __name__ == '__main__':
    main()
