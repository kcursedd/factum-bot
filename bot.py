import logging
import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from sherlock_mod import sherlock_search

TOKEN = os.environ.get("BOT_TOKEN", "ТВОЙ_ТОКЕН_СЮДА")

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔍 Factum OSINT bot\n"
        "Используй: /factum <username>\n"
        "Пример: /factum ivanov"
    )

async def factum_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажи ник. Пример: /factum target")
        return
    username = context.args[0].strip()
    msg = await update.message.reply_text(f"🔎 Ищем {username} по {len(sites)} сайтам...")
    results = await sherlock_search(username)
    if not results:
        await msg.edit_text("Ничего не найдено.")
        return
    response = f"*Factum* — результаты для `{username}`:\n\n"
    for site, url in results:
        response += f"✅ [{site}]({url})\n"
    await msg.edit_text(response, parse_mode="Markdown", disable_web_page_preview=True)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("factum", factum_command))
    logging.info("Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    # Загружаем базу сайтов
    import json
    with open("sites.json", "r", encoding="utf-8") as f:
        sites = json.load(f)
    main()