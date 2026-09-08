import json
import logging
import os
from pathlib import Path

import requests
from telegram import Update
from telegram.error import Forbidden
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("TOKEN")
API_URL = "https://open.er-api.com/v6/latest/USD"
YUBORISH_ORALIGI = 3600
OBUNACHILAR_FAYLI = Path(os.environ.get("OBUNACHILAR_FAYLI", "obunachilar.json"))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

obunachilar = set()


def obunachilarni_yuklash():
    if not OBUNACHILAR_FAYLI.exists():
        return set()
    try:
        return set(json.loads(OBUNACHILAR_FAYLI.read_text()))
    except (json.JSONDecodeError, OSError, TypeError):
        logger.warning("Obunachilar faylini o'qib bo'lmadi, bo'sh ro'yxat bilan boshlanadi.")
        return set()


def obunachilarni_saqlash():
    try:
        OBUNACHILAR_FAYLI.write_text(json.dumps(sorted(obunachilar)))
    except OSError as xato:
        logger.error("Obunachilarni saqlab bo'lmadi: %s", xato)


def kurslarni_olish():
    javob = requests.get(API_URL, timeout=10)
    javob.raise_for_status()
    data = javob.json()

    if data.get("result") != "success":
        raise ValueError(f"API xatosi: {data.get('error-type', 'nomalum')}")

    rates = data["rates"]
    usd_rub = rates["RUB"]
    usd_uzs = rates["UZS"]
    rub_uzs = usd_uzs / usd_rub

    return usd_rub, usd_uzs, rub_uzs


def kurs_matni():
    usd_rub, usd_uzs, rub_uzs = kurslarni_olish()
    return (
        f"💵 1 USD = {usd_uzs:,.2f} UZS\n"
        f"💵 1 USD = {usd_rub:,.2f} RUB\n"
        f"💶 1 RUB = {rub_uzs:,.2f} UZS"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    obunachilar.add(chat_id)
    obunachilarni_saqlash()
    await update.message.reply_text(
        "Salom! Endi sizga har soatda valyuta kurslari yuboriladi.\n"
        "Hozirgi kursni ko'rish uchun /kurs, to'xtatish uchun /stop yozing."
    )


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    obunachilar.discard(chat_id)
    obunachilarni_saqlash()
    await update.message.reply_text("Obuna bekor qilindi.")


async def kurs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(kurs_matni())
    except (requests.RequestException, ValueError, KeyError) as xato:
        logger.error("Kurslarni olishda xato: %s", xato)
        await update.message.reply_text("Kurslarni olishda xato yuz berdi. Keyinroq urinib ko'ring.")


async def yordam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - har soatlik kurs yuborilishiga obuna bo'lish\n"
        "/kurs - hozirgi kursni ko'rish\n"
        "/stop - obunani bekor qilish\n"
        "/help - shu ro'yxat"
    )


async def soatlik_yuborish(context: ContextTypes.DEFAULT_TYPE):
    if not obunachilar:
        return

    try:
        matn = kurs_matni()
    except (requests.RequestException, ValueError, KeyError) as xato:
        logger.error("Soatlik yuborish uchun kurslarni olib bo'lmadi: %s", xato)
        return

    for chat_id in list(obunachilar):
        try:
            await context.bot.send_message(chat_id=chat_id, text=matn)
        except Forbidden:
            logger.info("Chat %s botni bloklagan, obunadan chiqarildi.", chat_id)
            obunachilar.discard(chat_id)
            obunachilarni_saqlash()
        except Exception as xato:
            logger.error("Chat %s ga yuborib bo'lmadi: %s", chat_id, xato)


async def ishga_tushganda(application: Application):
    obunachilar.update(obunachilarni_yuklash())
    logger.info("%d ta obunachi yuklandi.", len(obunachilar))


def main():
    if not TOKEN:
        raise SystemExit(
            "TOKEN muhit o'zgaruvchisi topilmadi. @BotFather dan token oling va "
            "TOKEN=... qilib o'rnating."
        )

    application = ApplicationBuilder().token(TOKEN).post_init(ishga_tushganda).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("kurs", kurs))
    application.add_handler(CommandHandler("help", yordam))

    application.job_queue.run_repeating(
        soatlik_yuborish, interval=YUBORISH_ORALIGI, first=YUBORISH_ORALIGI
    )

    logger.info("Bot ishga tushdi.")
    application.run_polling()


if __name__ == "__main__":
    main()
