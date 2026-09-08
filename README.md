# Valyuta kursi Telegram boti

USD/UZS, USD/RUB va RUB/UZS kurslarini yuboradigan Telegram bot.
Kurslar [open.er-api.com](https://open.er-api.com) dan olinadi.

## Buyruqlar

| Buyruq | Vazifasi |
|--------|----------|
| `/start` | Har soatlik kurs yuborilishiga obuna bo'lish |
| `/kurs` | Hozirgi kursni darhol ko'rish |
| `/stop` | Obunani bekor qilish |
| `/help` | Buyruqlar ro'yxati |

## Ishga tushirish

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export TOKEN="@BotFather dan olingan token"
python bot.py
```

## Muhit o'zgaruvchilari

| O'zgaruvchi | Majburiy | Standart | Izoh |
|-------------|----------|----------|------|
| `TOKEN` | ha | — | @BotFather dan olingan bot tokeni |
| `OBUNACHILAR_FAYLI` | yo'q | `obunachilar.json` | Obunachilar ro'yxati saqlanadigan fayl |

Obunachilar ro'yxati diskka yoziladi, shuning uchun bot qayta ishga tushganda
obunalar saqlanib qoladi.
