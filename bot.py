import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import random
import string
from datetime import datetime

# ========== КОНФИГУРАЦИЯ ==========
BOT_TOKEN = "ВАШ_ТОКЕН_СЮДА"  # замените на токен от @BotFather
bot = telebot.TeleBot(BOT_TOKEN)
DB_NAME = "sherlock_355.db"

# ========== СОЗДАНИЕ БАЗЫ ДАННЫХ С 355 САЙТАМИ ==========
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Таблица сайтов (источников) - 355 штук
    c.execute('''CREATE TABLE IF NOT EXISTS sites (
        id INTEGER PRIMARY KEY,
        site_name TEXT UNIQUE,
        url TEXT
    )''')

    # Таблица людей
    c.execute('''CREATE TABLE IF NOT EXISTS persons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        phone TEXT,
        email TEXT,
        car_number TEXT,
        birth_date TEXT,
        address TEXT,
        passport TEXT,
        social_media TEXT
    )''')

    # Таблица связей "человек - сайт" (на каких сайтах пробито)
    c.execute('''CREATE TABLE IF NOT EXISTS person_site (
        person_id INTEGER,
        site_id INTEGER,
        FOREIGN KEY(person_id) REFERENCES persons(id),
        FOREIGN KEY(site_id) REFERENCES sites(id)
    )''')

    # Заполняем 355 сайтов, если их ещё нет
    c.execute("SELECT COUNT(*) FROM sites")
    if c.fetchone()[0] == 0:
        sites_data = []
        for i in range(1, 356):
            site_name = f"leak{str(i).zfill(3)}.ru"
            url = f"https://{site_name}/search"
            sites_data.append((site_name, url))
        c.executemany("INSERT INTO sites (site_name, url) VALUES (?, ?)", sites_data)
        print("✅ Добавлено 355 сайтов в базу.")

    # Заполняем тестовыми людьми (100 записей для демонстрации)
    c.execute("SELECT COUNT(*) FROM persons")
    if c.fetchone()[0] == 0:
        # Генерируем 100 фейковых профилей
        for _ in range(100):
            full_name = random.choice(['Иван Иванов','Петр Петров','Сидор Сидоров','Анна Смирнова','Елена Кузнецова','Дмитрий Соколов','Ольга Попова','Алексей Лебедев','Татьяна Козлова','Сергей Морозов']) + ' ' + str(random.randint(1,99))
            phone = '+7' + ''.join(random.choices(string.digits, k=10))
            email = ''.join(random.choices(string.ascii_lowercase, k=8)) + '@mail.ru'
            car_number = random.choice('АВЕКМНОРСТУХ') + ''.join(random.choices(string.digits, k=3)) + \
                         random.choice('АВЕКМНОРСТУХ') + random.choice('АВЕКМНОРСТУХ') + \
                         str(random.randint(1,199)).zfill(3)
            birth_date = f"{random.randint(1950,2010)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
            address = f"г. {random.choice(['Москва','СПб','Новосибирск','Екатеринбург','Казань'])}, ул. {random.choice(['Ленина','Пушкина','Гагарина'])}, д.{random.randint(1,100)}"
            passport = f"{random.randint(1000,9999)} {random.randint(100000,999999)}"
            social = f"vk.com/id{random.randint(1000,9999)}"
            c.execute('''INSERT INTO persons (full_name, phone, email, car_number, birth_date, address, passport, social_media)
                         VALUES (?,?,?,?,?,?,?,?)''',
                      (full_name, phone, email, car_number, birth_date, address, passport, social))
            person_id = c.lastrowid
            # Каждому человеку привязываем случайные 5-30 сайтов из 355
            num_sites = random.randint(5, 30)
            site_ids = random.sample(range(1, 356), num_sites)
            for sid in site_ids:
                c.execute("INSERT INTO person_site (person_id, site_id) VALUES (?, ?)", (person_id, sid))
        conn.commit()
        print("✅ Добавлено 100 тестовых профилей, каждый привязан к нескольким сайтам.")

    conn.close()

init_db()

# ========== ПОИСК В БАЗЕ ==========
def search_person(query, search_type):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if search_type == 'phone':
        c.execute("SELECT * FROM persons WHERE phone LIKE ? LIMIT 10", (f'%{query}%',))
    elif search_type == 'email':
        c.execute("SELECT * FROM persons WHERE email LIKE ? LIMIT 10", (f'%{query}%',))
    elif search_type == 'car_number':
        c.execute("SELECT * FROM persons WHERE car_number LIKE ? LIMIT 10", (f'%{query.upper()}%',))
    elif search_type == 'full_name':
        c.execute("SELECT * FROM persons WHERE full_name LIKE ? LIMIT 10", (f'%{query}%',))
    elif search_type == 'birth_date':
        c.execute("SELECT * FROM persons WHERE birth_date = ? LIMIT 10", (query,))
    else:
        return []
    persons = c.fetchall()
    results = []
    for p in persons:
        person_id = p[0]
        # получаем сайты для этого человека
        c.execute('''SELECT site_name FROM sites 
                     JOIN person_site ON sites.id = person_site.site_id 
                     WHERE person_site.person_id = ?''', (person_id,))
        sites = [row[0] for row in c.fetchall()]
        results.append((p, sites))
    conn.close()
    return results

def format_result(person, sites):
    (pid, full_name, phone, email, car_number, birth_date, address, passport, social_media) = person
    try:
        birth_fmt = datetime.strptime(birth_date, '%Y-%m-%d').strftime('%d.%m.%Y')
    except:
        birth_fmt = birth_date or 'не указана'
    sites_preview = ', '.join(sites[:10]) + (f' + ещё {len(sites)-10}' if len(sites) > 10 else '')
    return (f"📌 *РЕЗУЛЬТАТ ПРОБИВА*\n"
            f"┌─────────────────────\n"
            f"│ 👤 *ФИО:* {full_name}\n"
            f"│ 📞 *Телефон:* `{phone}`\n"
            f"│ 📧 *Email:* `{email}`\n"
            f"│ 🚗 *Авто:* `{car_number}`\n"
            f"│ 🎂 *Дата рождения:* {birth_fmt}\n"
            f"│ 🏠 *Адрес:* {address}\n"
            f"│ 🛂 *Паспорт:* {passport}\n"
            f"│ 🌐 *Соцсети:* {social_media}\n"
            f"│ 🌍 *Найден на {len(sites)} из 355 сайтов:*\n"
            f"│   {sites_preview}\n"
            f"└─────────────────────")

# ========== КЛАВИАТУРА ==========
def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("📞 По номеру телефона", callback_data="search_phone"),
        InlineKeyboardButton("📧 По email", callback_data="search_email"),
        InlineKeyboardButton("🚗 По номеру авто", callback_data="search_car"),
        InlineKeyboardButton("👤 По ФИО", callback_data="search_name"),
        InlineKeyboardButton("🎂 По дате рождения", callback_data="search_birth"),
        InlineKeyboardButton("❓ Помощь", callback_data="help")
    ]
    kb.add(*buttons)
    return kb

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     "🔍 *Бот «Шерлок» — пробив по 355 сайтам*\n"
                     "База данных содержит более 100 профилей и 355 источников утечек.\n"
                     "Выберите тип поиска:",
                     reply_markup=main_menu(),
                     parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "search_phone":
        bot.send_message(call.message.chat.id, "📞 Введите номер телефона (полный или часть):")
        bot.register_next_step_handler(call.message, process_phone)
    elif call.data == "search_email":
        bot.send_message(call.message.chat.id, "📧 Введите email (полный или часть):")
        bot.register_next_step_handler(call.message, process_email)
    elif call.data == "search_car":
        bot.send_message(call.message.chat.id, "🚗 Введите номер машины (пример: А123ВВ199):")
        bot.register_next_step_handler(call.message, process_car)
    elif call.data == "search_name":
        bot.send_message(call.message.chat.id, "👤 Введите ФИО (можно неполное):")
        bot.register_next_step_handler(call.message, process_name)
    elif call.data == "search_birth":
        bot.send_message(call.message.chat.id, "🎂 Введите дату рождения в формате ГГГГ-ММ-ДД:")
        bot.register_next_step_handler(call.message, process_birth)
    elif call.data == "help":
        bot.send_message(call.message.chat.id,
                         "🔎 *Инструкция*\n"
                         "1. Выберите категорию поиска.\n"
                         "2. Введите значение (можно часть).\n"
                         "3. Бот покажет до 10 совпадений и список из 355 сайтов, где найден человек.\n"
                         "⚠️ Данные тестовые. Для реального пробива замените базу на настоящие утечки.",
                         parse_mode='Markdown')
        bot.send_message(call.message.chat.id, "Меню:", reply_markup=main_menu())
    bot.answer_callback_query(call.id)

def process_phone(message):
    query = message.text.strip()
    if not query:
        bot.send_message(message.chat.id, "❌ Пустой запрос.", reply_markup=main_menu())
        return
    results = search_person(query, 'phone')
    send_results(message.chat.id, results, query)

def process_email(message):
    query = message.text.strip()
    if not query:
        bot.send_message(message.chat.id, "❌ Пустой запрос.", reply_markup=main_menu())
        return
    results = search_person(query, 'email')
    send_results(message.chat.id, results, query)

def process_car(message):
    query = message.text.strip().upper()
    if not query:
        bot.send_message(message.chat.id, "❌ Пустой запрос.", reply_markup=main_menu())
        return
    results = search_person(query, 'car_number')
    send_results(message.chat.id, results, query)

def process_name(message):
    query = message.text.strip()
    if not query:
        bot.send_message(message.chat.id, "❌ Пустой запрос.", reply_markup=main_menu())
        return
    results = search_person(query, 'full_name')
    send_results(message.chat.id, results, query)

def process_birth(message):
    query = message.text.strip()
    if not query:
        bot.send_message(message.chat.id, "❌ Пустой запрос.", reply_markup=main_menu())
        return
    try:
        datetime.strptime(query, '%Y-%m-%d')
    except:
        bot.send_message(message.chat.id, "❌ Неверный формат. Используйте ГГГГ-ММ-ДД", reply_markup=main_menu())
        return
    results = search_person(query, 'birth_date')
    send_results(message.chat.id, results, query)

def send_results(chat_id, results, query):
    if not results:
        bot.send_message(chat_id, f"🔍 По запросу `{query}` ничего не найдено в 355 сайтах.", parse_mode='Markdown')
    else:
        bot.send_message(chat_id, f"✅ *Найдено совпадений:* {len(results)} (из 100 профилей)", parse_mode='Markdown')
        for person, sites in results:
            bot.send_message(chat_id, format_result(person, sites), parse_mode='Markdown')
    bot.send_message(chat_id, "Выберите следующий поиск:", reply_markup=main_menu())

if __name__ == "__main__":
    print("Бот запущен. База содержит 355 сайтов и 100 профилей.")
    bot.infinity_polling()
