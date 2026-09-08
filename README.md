# Valyuta kursi Telegram boti

USD/UZS, USD/RUB va RUB/UZS kurslarini yuboradigan Telegram bot.
Kurslar [open.er-api.com](https://open.er-api.com) dan olinadi (API kaliti kerak emas).

## Buyruqlar

| Buyruq | Vazifasi |
|--------|----------|
| `/start` | Har soatlik kurs yuborilishiga obuna bo'lish |
| `/kurs` | Hozirgi kursni darhol ko'rish |
| `/stop` | Obunani bekor qilish |
| `/help` | Buyruqlar ro'yxati |

Namuna javob:

```
💵 1 USD = 12,150.00 UZS
💵 1 USD = 78.50 RUB
💶 1 RUB = 154.78 UZS
```

## 1-qadam: token olish

1. Telegramda [@BotFather](https://t.me/BotFather) ni oching
2. `/newbot` yuboring
3. Bot nomini kiriting (masalan `Kurs Bot`)
4. Username kiriting — `bot` bilan tugashi shart (masalan `mening_kurs_botim`)
5. BotFather `123456789:AAE...` ko'rinishidagi tokenni beradi — uni saqlab qo'ying

Ixtiyoriy, BotFather ichida buyruqlar ro'yxatini ham qo'shish mumkin —
`/setcommands` yuboring va quyidagini joylashtiring:

```
start - Har soatlik kursga obuna bo'lish
kurs - Hozirgi kursni ko'rish
stop - Obunani bekor qilish
help - Buyruqlar ro'yxati
```

## 2-qadam: sozlash va ishga tushirish

```bash
git clone https://github.com/nodirbetg/Telegram-bot
cd Telegram-bot

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # .env ichiga o'z tokeningizni yozing
python bot.py
```

Ishga tushganda quyidagi log chiqadi:

```
INFO - 0 ta obunachi yuklandi.
INFO - Bot ishga tushdi.
```

Endi Telegramda botingizga `/start` yuboring.

## Muhit o'zgaruvchilari

Tokenni `.env` fayl orqali ham, oddiy muhit o'zgaruvchisi orqali ham berish mumkin.
Muhit o'zgaruvchisi `.env` dan ustun turadi.

| O'zgaruvchi | Majburiy | Standart | Izoh |
|-------------|----------|----------|------|
| `TOKEN` | ha | — | @BotFather dan olingan bot tokeni |
| `YUBORISH_ORALIGI` | yo'q | `3600` | Kurs yuborish oralig'i, soniyada |
| `OBUNACHILAR_FAYLI` | yo'q | `obunachilar.json` | Obunachilar saqlanadigan fayl |

Obunachilar ro'yxati diskka yoziladi, shuning uchun bot qayta ishga tushganda
obunalar saqlanib qoladi.

## 24/7 ishlatish

Kompyuterda `python bot.py` qilib qoldirsangiz, kompyuter o'chganda bot ham
to'xtaydi. Doimiy ishlashi uchun quyidagilardan birini tanlang.
Repoda har uchala platforma uchun tayyor config bor — faqat GitHub bilan
kirib, `TOKEN` ni qo'shsangiz kifoya.

### Render (`render.yaml`)

1. [dashboard.render.com/select-repo?type=blueprint](https://dashboard.render.com/select-repo?type=blueprint)
2. Bu repoyni tanlang — Render `render.yaml` ni o'zi o'qiydi
3. `TOKEN` so'ralganda tokenni kiriting → **Apply**

Background worker Render'da pullik (starter ~$7/oy). Bepul reja faqat web
service uchun va u 15 daqiqadan keyin uxlab qoladi — polling bot uchun yaramaydi.

### Railway (`railway.json`)

1. [railway.com/new](https://railway.com/new) → **Deploy from GitHub repo**
2. Bu repoyni tanlang — Railway `Dockerfile` orqali quradi
3. **Variables** bo'limida `TOKEN` ni qo'shing → deploy

Trial kredit tugagach hobby reja ~$5/oy.

### Fly.io (`fly.toml`)

```bash
fly launch --no-deploy          # mavjud fly.toml ni ishlatadi
fly secrets set TOKEN="sizning_tokeningiz"
fly volumes create kurs_bot_data --size 1
fly deploy
```

`fly.toml` da volume sozlangan — obunachilar ro'yxati qayta deploy qilinganda
yo'qolmaydi. Karta biriktirish talab qilinadi, kichik bepul limit bor.

### Docker (o'z serveringizda)

```bash
docker build -t kurs-bot .
docker run -d --restart unless-stopped \
  -e TOKEN="sizning_tokeningiz" \
  -e OBUNACHILAR_FAYLI=/app/data/obunachilar.json \
  -v "$PWD/data:/app/data" \
  --name kurs-bot kurs-bot
```

### Linux serverda systemd

`/etc/systemd/system/kurs-bot.service`:

```ini
[Unit]
Description=Kurs Telegram bot
After=network-online.target

[Service]
WorkingDirectory=/opt/kurs-bot
EnvironmentFile=/opt/kurs-bot/.env
ExecStart=/opt/kurs-bot/.venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now kurs-bot
sudo journalctl -u kurs-bot -f
```

Butunlay bepul variant izlasangiz: **Oracle Cloud Free Tier** doimiy bepul VM
beradi (karta tekshiruvi bor, lekin pul yechilmaydi) — unda yuqoridagi systemd
usuli ishlaydi. Uydagi eski kompyuter yoki Raspberry Pi ham yetarli.

## Xatoliklar

| Xabar | Sabab |
|-------|-------|
| `TOKEN muhit o'zgaruvchisi topilmadi` | `.env` yo'q yoki ichida `TOKEN` yozilmagan |
| `telegram.error.InvalidToken` | Token noto'g'ri ko'chirilgan |
| `telegram.error.NetworkError` | Internet yo'q yoki Telegram bloklangan — VPN/proxy kerak |
| `Kurslarni olishda xato yuz berdi` | open.er-api.com javob bermayapti, keyinroq o'zi tiklanadi |
