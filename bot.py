from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Откройте расписание фестиваля!",
        reply_markup={"inline_keyboard": [[{"text": "Открыть расписание", "web_app": {"url": "http://localhost:5000"}}]]}
    )

if __name__ == "__main__":
    app = Application.builder().token("7099158898:AAFuPIsoi62BoCdVk3ChYclm8O35TdZMcgQ").build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()