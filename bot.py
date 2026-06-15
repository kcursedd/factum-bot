import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import psycopg2
from flask import Flask, request
import logging
from datetime import datetime
import random
import string

# === Переменные окружения (задаются в Render Dashboard) ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")   # Например: postgresql://user:pass@host:5432/db
WEBHOOK_URL = os.getenv("WEBHOOK_URL")     # Например: https://my-bot.onrender.com

if not all([BOT_TOKEN, DATABASE_URL, WEBHOOK_URL]):
    raise RuntimeError("Не все переменные окружения заданы!")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# === Работа с БД (PostgreSQL) ===
def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    """Создаёт таблицу и заполняет тестовыми данными (для демо). Замените на реальные данные."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS persons (
            id SERIAL PRIMARY KEY,
            phone TEXT,
            email TEXT,
            car_number TEXT,
            full_name TEXT,
            birth_date DATE,
            address TEXT,
            passport TEXT,
            social TEXT
        )
    """)
    cur.execute("SELECT COUNT(*) FROM persons")
    if cur.fetchone()[0] == 0:
        # Генерация 20 фейковых записей (удалите и загрузите реальные данные)
        for _ in range(20):
            phone = '+7' + ''.join(random.choices(string.digits, k=10))
            email = ''.join(random.choices(string.ascii_lowercase, k=8)) + '@mail.ru'
            car_number = random.choice('АВЕКМНОРСТУХ') + ''.join(random.choices(string.digits, k=3)) + random.choice('АВЕКМНОРСТУХ') + random.choice('АВЕКМНОРСТУХ') + str(random.randint(1,199)).zfill(3)
            full_name = random.choice(['Иван Иванов','Петр Петров','Сидор Сидоров','Анна Смирнова','Елена Кузнецова']) + ' ' + str(random.randint(1,99))
            birth_date = f"{random.randint(1950,2010)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
            address = f"г. Москва, ул. {random.choice(['Ленина','Пушкина','Гагарина'])}, д.{random.randint(1,100)}"
            passport = f"{random.randint(1000,9999)} {random.randint(100000,999999)}"
            social = f"vk.com/id{random.randint(1000,9999)}"
            cur.execute("""
                INSERT INTO persons (phone, email, car_number, full_name, birth_date, address, passport, social)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (phone, email, car_number, full_name, birth_date, address, passport, social))
        conn.commit()
    cur.close()
    conn.close()

init_db()  # автоматически при каждом запуске (быстро, таблица уже существует)

# === Поиск в БД ===
def search_person(query, search_type):
    conn = get_db_connection()
    cur = conn.cursor()
    if search_type == 'phone':
        cur.execute("SELECT * FROM persons WHERE phone LIKE %s", (f'%{query}%',))
    elif search_type == 'email':
        cur.execute("SELECT * FROM persons WHERE email LIKE %s", (f'%{query}%',))
    elif search_type == 'car_number':
        cur.execute("SELECT * FROM persons WHERE car_number LIKE %s", (f'%{query.upper()}%',))
    elif search_type == 'full_name':
        cur.execute("SELECT * FROM persons WHERE full_name LIKE %s", (f'%{query}%',))
    elif search_type == 'birth_date':
        cur.execute("SELECT * FROM persons WHERE birth_date = %s", (query,))
    else:
        return []
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

def format_result(record):
    (_, phone, email, car_number, full_name, birth_date, address, passport, social) = record
    birth_fmt = birth_date.strftime('%d.%m.%Y') if birth_date else 'не указано'
    return (f"📌 *Результат пробива*\n"
            f"┌─────────────────────\n"
            f"│ 👤 *ФИО:* {full_name}\n"
            f"│ 📞 *Телефон:* `{phone}`\n"
            f"│ 📧 *Email:* `{email}`\n"
            f"│ 🚗 *Номер авто:* `{car_number}`\n"
            f"│ 🎂 *Дата рождения:* {birth_fmt}\n"
            f"│ 🏠 *Адрес:* {address}\n"
            f"│ 🛂 *Паспорт:* {passport}\n"
            f"│ 🌐 *Соцсети:* {social}\n"
            f"└─────────────────────")

# === Клавиатура ===
def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📞 По номеру телефона", callback_data="search_phone"),
        InlineKeyboardButton("📧 По email", callback_data="search_email"),
        InlineKeyboardButton("🚗 По номеру машины", callback_data="search_car"),
        InlineKeyboardButton("👤 По ФИО", callback_data="search_name"),
        InlineKeyboardButton("🎂 По дате рождения", callback_data="search_birth"),
        InlineKeyboardButton("❓ Помощь", callback_data="help")
    )
    return kb

# === Обработчики ===
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "search_phone":
        bot.send_message(call.message.chat.id, "📞 Введите номер телефона (полный или часть):")
        bot.register_next_step_handler(call.message, lambda m: process_search(m, 'phone'))
    elif call.data == "search_email":
        bot.send_message(call.message.chat.id, "📧 Введите email:")
        bot.register_next_step_handler(call.message, lambda m: process_search(m, 'email'))
    elif call.data == "search_car":
        bot.send_message(call.message.chat.id, "🚗 Введите номер машины (пример: А123ВВ199):")
        bot.register_next_step_handler(call.message, lambda m: process_search(m, 'car_number'))
    elif call.data == "search_name":
        bot.send_message(call.message.chat.id, "👤 Введите ФИО (можно неполное):")
        bot.register_next_step_handler(call.message, lambda m: process_search(m, 'full_name'))
    elif call.data == "search_birth":
        bot.send_message(call.message.chat.id, "🎂 Введите дату рождения в формате ГГГГ-ММ-ДД:")
        bot.register_next_step_handler(call.message, lambda m: process_search(m, 'birth_date'))
    elif call.data == "help":
        bot.send_message(call.message.chat.id, "🔎 *Инструкция*\nВыберите тип данных → введите значение → получите результат.\n*Для реального пробива замените тестовую БД на настоящие утечки.*", parse_mode='Markdown')
    bot.answer_callback_query(call.id)

def process_search(message, search_type):
    query = message.text.strip()
    if not query:
        bot.send_message(message.chat.id, "❌ Пустой запрос. Попробуйте снова.")
        return
    if search_type == 'birth_date':
        try:
            datetime.strptime(query, '%Y-%m-%d')
        except:
            bot.send_message(message.chat.id, "❌ Неверный формат. Используйте ГГГГ-ММ-ДД")
            return
    results = search_person(query, search_type)
    if not results:
        bot.send_message(message.chat.id, f"🔍 По запросу `{query}` ничего не найдено.", parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, f"✅ Найдено записей: {len(results)}", parse_mode='Markdown')
        for r in results:
            bot.send_message(message.chat.id, format_result(r), parse_mode='Markdown')
    bot.send_message(message.chat.id, "Выберите следующий поиск:", reply_markup=main_menu())

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.send_message(message.chat.id, "🔍 *Бот «Шерлок» на Render + GitHub*\nГотов пробивать по телефонам, email, авто, ФИО, дате рождения.", reply_markup=main_menu(), parse_mode='Markdown')

# === Flask для вебхука ===
@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
        bot.process_new_updates([update])
        return '', 200
    return '', 403

@app.route('/')
def index():
    return "Бот работает", 200

def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + '/' + BOT_TOKEN)

if __name__ == '__main__':
    set_webhook()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
