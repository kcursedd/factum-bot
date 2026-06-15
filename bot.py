import logging, os, asyncio, aiohttp, json, time, random
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ================= ВСТРОЕННАЯ БАЗА САЙТОВ (355) =================
SITES_JSON = r"""
[
  {"name":"9GAG","url":"https://9gag.com/u/{}","urlMain":"https://9gag.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"About.me","url":"https://about.me/{}","urlMain":"https://about.me/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  ... (здесь весь остальной JSON, как раньше, без изменений) ...
  {"name":"YouTube","url":"https://www.youtube.com/@{}","urlMain":"https://www.youtube.com/","username_claimed":"blue","errorType":"status_code","errorCode":404},
  {"name":"Zillow","url":"https://www.zillow.com/profile/{}","urlMain":"https://www.zillow.com/","username_claimed":"blue","errorType":"status_code","errorCode":404}
]
"""
# (для краткости я не дублирую все 355 записей, они остаются те же, что и в предыдущем ответе)

sites = json.loads(SITES_JSON)
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не задан!")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# ================= ФУНКЦИИ ПОИСКА =================
async def check_site(session, site_info, username):
    name = site_info["name"]
    url = site_info["url"].format(username)
    try:
        async with session.get(url, timeout=10, allow_redirects=True) as resp:
            if resp.status == 200:
                return (name, url)
    except:
        pass
    return None

async def sherlock_search(username):
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        tasks = [check_site(session, site, username) for site in sites]
        results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]

# ================= ЭМУЛЯЦИЯ ДАННЫХ (заглушки) =================
# Для демонстрации генерируем правдоподобный ответ, используя введённый параметр
# В реальности здесь должны быть запросы к API или БД

def emulate_phone_search(phone):
    return f"""📱 Информация по номеру: {phone}
├ Оператор: Т2 Мобайл
├ Регион: Воронежская область
└ Страна: Россия

👤 Основные данные
├ ФИО: Баранов Сергей Валентинович
├ Дата рождения: 16.10.1957
└ Возраст: 68

🔎 Телефонные книги: PErEd0zz, Кирилл, Кирюха, Lirika

🧑‍💻 Вконтакте: Павел Салманов (https://vk.com/id70568545)
👨‍🦳 Одноклассники: илья фатеев (https://ok.ru/profile/569614147987)
💬 Telegram: @liz1xls, @GOLOBA_B_KPOBU
📧 E-mail: salmanov.p@mail.ru, ilya-fateev-00@mail.ru"""

def emulate_email_search(email):
    return f"""📧 Информация по email: {email}
├ Утечки: 2 базы
├ Связанные номера: +79518673646, +79151234567
├ Имя: Илья Фатеев
└ Nickname: fateev20010"""

def emulate_passport_search(passport):
    return f"""📄 Паспорт: {passport}
├ Выдан: ОВД г. Воронеж
├ Дата выдачи: 12.05.2010
├ ФИО: Фатеев Илья Алексеевич
└ Прописка: г. Воронеж, ул. Ленина, д. 10"""

def emulate_snils_search(snils):
    return f"""📄 СНИЛС: {snils}
├ ФИО: Фатеев Илья Алексеевич
├ Дата рождения: 02.10.2004
└ Статус: действует"""

def emulate_inn_search(inn):
    return f"""📄 ИНН: {inn}
├ ФИО: Фатеев Илья Алексеевич
├ Регион: Воронежская область
└ Организации: ИП Фатеев И.А."""

def emulate_vu_search(vu):
    return f"""🚗 Водительские права: {vu}
├ ФИО: Фатеев Илья Алексеевич
├ Дата рождения: 02.10.2004
├ Категории: B, B1, M
└ Выдано: ГИБДД 3604"""

def emulate_adr_search(adr):
    return f"""🏠 Адрес: {adr}
├ Кадастровый номер: 36:34:0401015:1234
├ Площадь: 54.2 м²
├ Собственник: Фатеев Илья Алексеевич
└ Обременения: нет"""

def emulate_vin_search(vin):
    return f"""🚘 VIN: {vin}
├ Марка: ВАЗ 2114
├ Год: 2010
├ Цвет: серебристый
├ Владелец: Фатеев Илья Алексеевич
└ ДТП: 1 (15.07.2022)"""

def emulate_photo_reply():
    return "📸 Поиск по фото временно недоступен (заглушка)"

# ================= ОБРАБОТЧИКИ КОМАНД =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🕵️‍♂️ <b>Factum — продвинутый поиск по цифровым следам</b>\n\n"
        "<b>📋 Категории поиска:</b>\n"
        "▸ 👤 Личность\n"
        "▸ 📞 Контакты\n"
        "▸ 🚗 Транспорт\n"
        "▸ 🌐 Социальные сети\n"
        "▸ 📟 Telegram\n"
        "▸ 📄 Документы\n"
        "▸ 🔍 Онлайн‑следы\n"
        "▸ 🏠 Недвижимость\n"
        "▸ 🏢 Юрлица\n"
        "▸ 📸 Фото\n\n"
        "<b>⚡ Быстрые команды:</b>\n"
        "/phone <номер> — поиск по телефону\n"
        "/email <email> — поиск по почте\n"
        "/passport <серия номер> — паспорт\n"
        "/snils <номер> — СНИЛС\n"
        "/inn <физ. ИНН> — ИНН физлица\n"
        "/vu <номер прав> — водительские права\n"
        "/adr <адрес> — недвижимость\n"
        "/vin <VIN> — автомобиль\n"
        "/factum <никнейм> — пробив по 355 сайтам\n"
        "/photo — поиск по фото (отправьте изображение)"
    )
    await update.message.reply_text(text, parse_mode="HTML")

# Обработчики с эмуляцией
async def phone_cmd(update, context):
    if not context.args:
        await update.message.reply_text("⚠️ Укажите номер телефона: /phone 79991234567")
        return
    phone = context.args[0]
    await update.message.reply_text(emulate_phone_search(phone), parse_mode="HTML")

async def email_cmd(update, context):
    if not context.args:
        await update.message.reply_text("⚠️ Укажите email: /email user@mail.ru")
        return
    email = context.args[0]
    await update.message.reply_text(emulate_email_search(email), parse_mode="HTML")

async def passport_cmd(update, context):
    if not context.args:
        await update.message.reply_text("⚠️ Укажите паспорт: /passport 4510123456")
        return
    passport = context.args[0]
    await update.message.reply_text(emulate_passport_search(passport), parse_mode="HTML")

async def snils_cmd(update, context):
    if not context.args:
        await update.message.reply_text("⚠️ Укажите СНИЛС: /snils 12345678901")
        return
    snils = context.args[0]
    await update.message.reply_text(emulate_snils_search(snils), parse_mode="HTML")

async def inn_cmd(update, context):
    if not context.args:
        await update.message.reply_text("⚠️ Укажите ИНН: /inn 2540214547")
        return
    inn = context.args[0]
    await update.message.reply_text(emulate_inn_search(inn), parse_mode="HTML")

async def vu_cmd(update, context):
    if not context.args:
        await update.message.reply_text("⚠️ Укажите номер прав: /vu 1234567890")
        return
    vu = context.args[0]
    await update.message.reply_text(emulate_vu_search(vu), parse_mode="HTML")

async def adr_cmd(update, context):
    if not context.args:
        await update.message.reply_text("⚠️ Укажите адрес: /adr Воронеж, Ленина 1")
        return
    adr = " ".join(context.args)
    await update.message.reply_text(emulate_adr_search(adr), parse_mode="HTML")

async def vin_cmd(update, context):
    if not context.args:
        await update.message.reply_text("⚠️ Укажите VIN: /vin XTA211440C5106924")
        return
    vin = context.args[0]
    await update.message.reply_text(emulate_vin_search(vin), parse_mode="HTML")

# Рабочая команда поиска по нику
async def factum_cmd(update, context):
    if not context.args:
        await update.message.reply_text("⚠️ Укажите ник: /factum target")
        return
    username = context.args[0].strip()
    msg = await update.message.reply_text(f"🔎 Ищем <b>{username}</b> по {len(sites)} сайтам...", parse_mode="HTML")
    start_time = time.time()
    results = await sherlock_search(username)
    elapsed = round(time.time() - start_time, 2)
    if not results:
        await msg.edit_text(f"❌ Ничего не найдено для <b>{username}</b>.\nПроверено {len(sites)} сайтов за {elapsed}с.", parse_mode="HTML")
        return
    found = len(results)
    resp = f"🎯 <b>Factum — результаты для</b> <code>{username}</code>\n📊 Найдено: {found} / {len(sites)}\n⏱ Время: {elapsed}с\n\n"
    for site, url in results:
        resp += f"✅ <a href='{url}'>{site}</a>\n"
    if len(resp) > 4096:
        resp = resp[:4000] + "\n... (обрезано)"
    await msg.edit_text(resp, parse_mode="HTML", disable_web_page_preview=True)

async def photo_cmd(update, context):
    await update.message.reply_text(emulate_photo_reply(), parse_mode="HTML")

# ================= ЗАПУСК =================
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("factum", factum_cmd))
    app.add_handler(CommandHandler("phone", phone_cmd))
    app.add_handler(CommandHandler("email", email_cmd))
    app.add_handler(CommandHandler("passport", passport_cmd))
    app.add_handler(CommandHandler("snils", snils_cmd))
    app.add_handler(CommandHandler("inn", inn_cmd))
    app.add_handler(CommandHandler("vu", vu_cmd))
    app.add_handler(CommandHandler("adr", adr_cmd))
    app.add_handler(CommandHandler("vin", vin_cmd))
    app.add_handler(CommandHandler("photo", photo_cmd))
    logger.info("✅ Factum бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
