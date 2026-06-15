import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import random
import string
from datetime import datetime

# ========== КОНФИГ ==========
BOT_TOKEN = "ВАШ_ТОКЕН_СЮДА"  # замените на токен от @BotFather
bot = telebot.TeleBot(BOT_TOKEN)

# ========== БАЗА ДАННЫХ (SQLite) ==========
DB_NAME = "sherlock.db"

def init_db():
    """Создаёт таблицу и заполняет тестовыми данными (20 записей)"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS persons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT,
        email TEXT,
        car_number TEXT,
        full_name TEXT,
        birth_date TEXT,
        address TEXT,
        passport TEXT,
        social TEXT
    )''')
    # Проверяем, пустая ли таблица
    c.execute("SELECT COUNT(*) FROM persons")
    if c.fetchone()[0] == 0:
        # Генерируем 20 фейковых, но правдоподобных записей
        for _ in range(20):
            phone = '+7' + ''.join(random.choices(string.digits, k=10))
            email = ''.join(random.choices(string.ascii_lowercase, k=8)) + '@example.com'
            car_number = random.choice('АВЕКМНОРСТУХ') + ''.join(random.choices(string.digits, k=3)) + \
                         random.choice('АВЕКМНОРСТУХ') + random.choice('АВЕКМНОРСТУХ') + \
                         str(random.randint(1, 199)).zfill(3)
            names = ['Иван Иванов', 'Петр Петров', 'Сидор Сидоров', 'Анна Смирнова', 'Елена Кузнецова',
                     'Дмитрий Соколов', 'Ольга Попова', 'Алексей Лебедев', 'Татьяна Козлова']
            full_name = random.choice(names) + ' ' + str(random.randint(1, 99))
            birth_date = f"{random.randint(1950, 2010)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
            address = f"г. {random.choice(['Москва','СПб','Новосибирск','Екатеринбург','Казань'])}, ул. {random.choice(['Ленина','Пушкина','Гагарина','Советская'])}, д.{random.randint(1,100)}"
            passport = f"{random.randint(1000,9999)} {random.randint(100000,999999)}"
            social = f"vk.com/id{random.randint(1000,9999)}"
            c.execute("INSERT INTO persons (phone, email, car_number, full_name, birth_date, address, passport, social) VALUES (?,?,?,?,?,?,?,?)",
                      (phone, email, car_number, full_name, birth_date, address, passport, social))
        conn.commit()
    conn.close()

init_db()

def search_person(query, search_type):
    """Поиск в БД по типу"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if search_type == 'phone':
        c.execute("SELECT * FROM persons WHERE phone LIKE ?", (f'%{query}%',))
    elif search_type == 'email':
        c.execute("SELECT * FROM persons WHERE email LIKE ?", (f'%{query}%',))
    elif search_type == 'car_number':
        c.execute("SELECT * FROM persons WHERE car_number LIKE ?", (f'%{query.upper()}%',))
    elif search_type == 'full_name':
        c.execute("SELECT * FROM persons WHERE full_name LIKE ?", (f'%{query}%',))
    elif search_type == 'birth_date':
        c.execute("SELECT * FROM persons WHERE birth_date = ?", (query,))
    else:
        return []
    results = c.fetchall()
    conn.close()
    return results

def format_result(record):
    """Красивое оформление одной записи"""
    (_, phone, email, car_number, full_name, birth_date, address, passport, social) = record
    try:
        birth_fmt = datetime.strptime(birth_date, '%Y-%m-%d').strftime('%d.%m.%Y')
    except:
        birth_fmt = birth_date or 'не указано'
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

def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("📞 По номеру телефона", callback_data="search_phone"),
        InlineKeyboardButton("📧 По email", callback_data="search_email"),
        InlineKeyboardButton("🚗 По номеру машины", callback_data="search_car"),
        InlineKeyboardButton("👤 По ФИО", callback_data="search_name"),
        InlineKeyboardButton("🎂 По дате рождения", callback_data="search_birth"),
        InlineKeyboardButton("❓ Помощь", callback_data="help")
    ]
    keyboard.add(*buttons)
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     "🔍 *Бот «Шерлок» v2.0*\nРежим: поиск по базам данных.\nВыберите тип поиска:",
                     reply_markup=main_menu(),
                     parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "search_phone":
        bot.send_message(call.message.chat.id, "📞 Введите номер телефона (полностью или часть):")
        bot.register_next_step_handler(call.message, process_phone)
    elif call.data == "search_email":
        bot.send_message(call.message.chat.id, "📧 Введите email (полностью или часть):")
        bot.register_next_step_handler(call.message, process_email)
    elif call.data == "search_car":
        bot.send_message(call.message.chat.id, "🚗 Введите номер машины (пример: А123ВВ199):")
        bot.register_next_step_handler(call.message, process_car)
    elif call.data == "search_name":
        bot.send_message(call.message.chat.id, "👤 Введите ФИО (можно неполное, например 'Иван'):")
        bot.register_next_step_handler(call.message, process_name)
    elif call.data == "search_birth":
        bot.send_message(call.message.chat.id, "🎂 Введите дату рождения в формате ГГГГ-ММ-ДД:")
        bot.register_next_step_handler(call.message, process_birth)
    elif call.data == "help":
        bot.send_message(call.message.chat.id,
                         "🔎 *Инструкция*\nВыберите категорию → введите значение → получите все совпадения.\n"
                         "📂 В базе 20 демо-записей. Для реального пробива замените базу на свои данные.",
                         parse_mode='Markdown')
    bot.answer_callback_query(call.id)

def process_phone(message):
    query = message.text.strip()
    if not query:
        bot.send_message(message.chat.id, "❌ Пустой запрос.")
        return
    results = search_person(query, 'phone')
    send_results(message.chat.id, results, query)

def process_email(message):
    query = message.text.strip()
    if not query:
        bot.send_message(message.chat.id, "❌ Пустой запрос.")
        return
    results = search_person(query, 'email')
    send_results(message.chat.id, results, query)

def process_car(message):
    query = message.text.strip().upper()
    if not query:
        bot.send_message(message.chat.id, "❌ Пустой запрос.")
        return
    results = search_person(query, 'car_number')
    send_results(message.chat.id, results, query)

def process_name(message):
    query = message.text.strip()
    if not query:
        bot.send_message(message.chat.id, "❌ Пустой запрос.")
        return
    results = search_person(query, 'full_name')
    send_results(message.chat.id, results, query)

def process_birth(message):
    query = message.text.strip()
    if not query:
        bot.send_message(message.chat.id, "❌ Пустой запрос.")
        return
    # валидация формата
    try:
        datetime.strptime(query, '%Y-%m-%d')
    except:
        bot.send_message(message.chat.id, "❌ Неверный формат. Используйте ГГГГ-ММ-ДД (например, 1990-05-15)")
        return
    results = search_person(query, 'birth_date')
    send_results(message.chat.id, results, query)

def send_results(chat_id, results, query):
    if not results:
        bot.send_message(chat_id, f"🔍 По запросу `{query}` ничего не найдено.", parse_mode='Markdown')
    else:
        bot.send_message(chat_id, f"✅ Найдено записей: {len(results)}", parse_mode='Markdown')
        for r in results:
            bot.send_message(chat_id, format_result(r), parse_mode='Markdown')
    bot.send_message(chat_id, "Выберите следующий поиск:", reply_markup=main_menu())

if __name__ == "__main__":
    print("Бот запущен. Нажми Ctrl+C для остановки.")
    bot.infinity_polling()
