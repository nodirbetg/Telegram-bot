import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("TOKEN")

obunachilar = set()

def kurslarni_olish():
    javob = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10)
    data = javob.json()
    rates = data["rates"]

    usd_rub = rates["RUB"]
    usd_uzs = rates["UZS"]
    rub_uzs = usd_uzs / usd_rub

    return usd_rub, usd_uzs, rub_uzs

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    obunachilar.add(chat_id)
    await update.message.reply_text(
        "Salom! Endi sizga har soatda valyuta kurslari yuboriladi.\n"
        "To'xtatish uchun /stop yozing."
    )

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    obunachilar.discard(chat_id)
    await update.message.reply_text("Obuna bekor qilindi.")

async def kurs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        usd_rub, usd_uzs, rub_uzs = kurslarni_olish()
        matn = (
            f"💵 1 USD = {usd
