# 45-sonli «Nurli maskan» maktab-internati — Telegram murojaatlar boti

## Imkoniyatlar
- O'quvchi, ota-ona, maktab xodimi va boshqa fuqarolardan murojaat qabul qilish
- Ism-familiya va telefon raqamini majburiy kiritish
- Ariza, taklif va shikoyat turini tanlash
- Matn, rasm yoki hujjat qabul qilish
- Har bir murojaatga raqam berish va SQLite bazasida saqlash
- Murojaatni qabul qilgan guruh administratorlari holatni yangilashi
- Foydalanuvchi o'z murojaatining holatini bot orqali tekshirishi

## 1. Kerak bo'ladigan ma'lumotlar
1. BotFather tokeni.
2. Mavjud Telegram guruhining chat ID raqami (`-100...` ko'rinishida).

Tokenni hech kimga yubormang va ommaga ko'rsatmang.

## 2. Guruh ID raqamini olish
1. Bot guruhda administrator bo'lib tursin.
2. Bot ishga tushgandan keyin guruh ichida `/groupid` buyrug'ini yuboring.
3. Dastlab `.env` faylida `GROUP_ID=0` deb qoldiring va botni ishga tushiring.
4. Guruh ichida `/groupid` buyrug'ini yuboring. Bot javobida `-100...` bilan boshlanadigan ID chiqadi.
5. Botni to'xtating, `.env` faylidagi `GROUP_ID=0` o'rniga chiqqan raqamni yozing va botni qayta ishga tushiring.
6. Bot guruhga xabar yubora olishi uchun guruhda xabar yuborish huquqi bo'lishi kerak.

## 3. O'rnatish (Windows / macOS / Linux)
Python 3.10 yoki yangiroq versiyasini o'rnating. Loyiha papkasida terminal ochib:
```bash
python -m venv .venv
```
Windows:
```bash
.venv\Scripts\activate
```
macOS/Linux:
```bash
source .venv/bin/activate
```
So'ng:
```bash
pip install -r requirements.txt
```
`.env.example` faylidan nusxa olib `.env` deb nomlang va `BOT_TOKEN` hamda `GROUP_ID` qiymatlarini kiriting.
Ishga tushirish:
```bash
python bot.py
```

## 4. Telefon va kompyuterda doimiy ishlashi
Telefon yoki kompyuterdagi Telegram ilovasidan botdan foydalanish mumkin. Lekin botning o'zi 24/7 ishlashi uchun kompyuter doim yoqilgan bo'lishi yoki Python qo'llaydigan hosting/serverga joylashtirilishi kerak. Telefonning o'zida ishga tushirish doimiy va ishonchli hosting o'rnini bosmaydi.

## 5. Muhim xavfsizlik eslatmalari
- Bot tokenini chatga, guruhga yoki ommaviy repozitoriyga yubormang.
- Murojaatlarda shaxsiy ma'lumotlar bo'lishi mumkin. Guruhga faqat murojaatlarni ko'rishi shart bo'lgan mas'ul xodimlarni qo'shing.
- Murojaatlar bazasi (`murojaatlar.db`) muntazam zaxiralansin va unga kirish cheklansin.
- Ishga tushirishdan oldin maktab rahbariyati bilan ma'lumotlarni saqlash muddati va murojaatlarni ko'rish vakolatlarini kelishib oling.

## 6. Cheklov
Bu boshlang'ich ishchi versiya. Javob matnini murojaatchiga yuborish, hisobot eksporti, rollar va kengaytirilgan audit jurnali keyingi bosqichda qo'shilishi mumkin.
