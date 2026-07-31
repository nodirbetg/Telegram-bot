import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Men sizning birinchi botingizman.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    matn = update.message.text
    await update.message.reply_text(f"Siz yozdingiz: {matn}")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

print("Bot ishga tushdi...")
app.run_polling()
