import os
import asyncio
import sqlite3
from datetime import datetime
from html import escape
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN", "").strip()
GROUP_ID = os.getenv("GROUP_ID", "0").strip()
DB_PATH = os.getenv("DB_PATH", "murojaatlar.db")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN .env faylida to'ldirilishi kerak.")
GROUP_ID = int(GROUP_ID)

bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

class Form(StatesGroup):
    category = State()
    fullname = State()
    phone = State()
    kind = State()
    body = State()
    attachment = State()

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS appeals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            fullname TEXT NOT NULL,
            phone TEXT NOT NULL,
            kind TEXT NOT NULL,
            body TEXT NOT NULL,
            attachment_file_id TEXT,
            attachment_type TEXT,
            status TEXT NOT NULL DEFAULT 'Yangi',
            created_at TEXT NOT NULL,
            group_message_id INTEGER
        )
        """)

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✍️ Murojaat yuborish")],
            [KeyboardButton(text="🔎 Murojaat holatini tekshirish")],
            [KeyboardButton(text="ℹ️ Ma'lumot")]
        ], resize_keyboard=True
    )

def options(items):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=x)] for x in items] +
                 [[KeyboardButton(text="⬅️ Bekor qilish")]],
        resize_keyboard=True
    )

def status_keyboard(appeal_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🟡 Ko'rib chiqilmoqda", callback_data=f"st:{appeal_id}:Ko'rib chiqilmoqda"),
            InlineKeyboardButton(text="🟢 Hal qilindi", callback_data=f"st:{appeal_id}:Hal qilindi")
        ]
    ])

async def is_group_admin(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(GROUP_ID, user_id)
        return member.status in ("administrator", "creator")
    except Exception:
        return False

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Assalomu alaykum!\n"
        "<b>45-sonli «Nurli maskan» maktab-internati</b>\n"
        "murojaatlar botiga xush kelibsiz.\n\n"
        "Bu bot orqali ariza, taklif va shikoyat yuborishingiz mumkin. "
        "Murojaat yuborishda ism-familiya va telefon raqami talab qilinadi.",
        reply_markup=main_menu()
    )

@dp.message(Command("id"))
async def get_id(message: Message):
    await message.answer(f"Sizning Telegram ID raqamingiz: <code>{message.from_user.id}</code>")

@dp.message(Command("groupid"))
async def get_group_id(message: Message):
    if message.chat.type in ("group", "supergroup"):
        await message.answer(f"Ushbu guruhning ID raqami: <code>{message.chat.id}</code>")
    else:
        await message.answer("Bu buyruqni murojaatlar guruhining ichida yuboring.")

@dp.message(F.text == "✍️ Murojaat yuborish")
async def begin(message: Message, state: FSMContext):
    await state.set_state(Form.category)
    await message.answer("Murojaatchi toifasini tanlang:", reply_markup=options([
        "O'quvchi", "Ota-ona", "Maktab xodimi", "Boshqa fuqaro"
    ]))

@dp.message(F.text == "⬅️ Bekor qilish")
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Murojaat yuborish bekor qilindi.", reply_markup=main_menu())

@dp.message(Form.category)
async def category(message: Message, state: FSMContext):
    allowed = ["O'quvchi", "Ota-ona", "Maktab xodimi", "Boshqa fuqaro"]
    if message.text not in allowed:
        return await message.answer("Iltimos, ro'yxatdan toifani tanlang.")
    await state.update_data(category=message.text)
    await state.set_state(Form.fullname)
    await message.answer("Ism va familiyangizni to'liq kiriting:", reply_markup=ReplyKeyboardRemove())

@dp.message(Form.fullname)
async def fullname(message: Message, state: FSMContext):
    value = (message.text or "").strip()
    if len(value.split()) < 2 or len(value) < 5:
        return await message.answer("Iltimos, ism va familiyangizni to'liq kiriting.")
    await state.update_data(fullname=value)
    await state.set_state(Form.phone)
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon raqamimni yuborish", request_contact=True)],
                  [KeyboardButton(text="⬅️ Bekor qilish")]],
        resize_keyboard=True
    )
    await message.answer(
        "Telefon raqamingizni yuboring. Tugma orqali kontaktni ulashishingiz yoki "
        "+998901234567 shaklida yozishingiz mumkin.", reply_markup=kb
    )

@dp.message(Form.phone)
async def phone(message: Message, state: FSMContext):
    if message.contact:
        number = message.contact.phone_number
    else:
        number = (message.text or "").strip()
        digits = "".join(ch for ch in number if ch.isdigit())
        if len(digits) < 9:
            return await message.answer("Telefon raqami noto'g'ri. Masalan: +998901234567")
    await state.update_data(phone=number)
    await state.set_state(Form.kind)
    await message.answer("Murojaat turini tanlang:", reply_markup=options([
        "Ariza", "Taklif", "Shikoyat"
    ]))

@dp.message(Form.kind)
async def kind(message: Message, state: FSMContext):
    if message.text not in ["Ariza", "Taklif", "Shikoyat"]:
        return await message.answer("Iltimos, Ariza, Taklif yoki Shikoyat turini tanlang.")
    await state.update_data(kind=message.text)
    await state.set_state(Form.body)
    await message.answer("Murojaatingiz mazmunini batafsil yozing:", reply_markup=ReplyKeyboardRemove())

@dp.message(Form.body)
async def body(message: Message, state: FSMContext):
    value = (message.text or "").strip()
    if len(value) < 5:
        return await message.answer("Murojaat matni juda qisqa. Iltimos, batafsilroq yozing.")
    await state.update_data(body=value)
    await state.set_state(Form.attachment)
    await message.answer(
        "Agar kerak bo'lsa, rasm yoki hujjat yuboring. Biriktirma bo'lmasa, "
        "«Yuborish» tugmasini bosing.",
        reply_markup=options(["Yuborish"])
    )

@dp.message(Form.attachment)
async def attachment(message: Message, state: FSMContext):
    if message.text == "Yuborish":
        file_id, file_type = None, None
    elif message.photo:
        file_id, file_type = message.photo[-1].file_id, "photo"
    elif message.document:
        file_id, file_type = message.document.file_id, "document"
    else:
        return await message.answer("Rasm yoki hujjat yuboring, yoki «Yuborish» tugmasini bosing.")
    data = await state.get_data()
    with db() as con:
        cur = con.execute(
            """INSERT INTO appeals
            (user_id, category, fullname, phone, kind, body, attachment_file_id,
             attachment_type, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (message.from_user.id, data["category"], data["fullname"], data["phone"],
             data["kind"], data["body"], file_id, file_type,
             datetime.now().strftime("%Y-%m-%d %H:%M"))
        )
        appeal_id = cur.lastrowid

    text = (
        f"🏫 <b>45-sonli «Nurli maskan» maktab-internati</b>\n"
        f"📩 <b>YANGI MUROJAAT №{appeal_id:04d}</b>\n\n"
        f"<b>Murojaatchi:</b> {escape(data['fullname'])}\n"
        f"<b>Toifasi:</b> {escape(data['category'])}\n"
        f"<b>Telefon:</b> {escape(data['phone'])}\n"
        f"<b>Turi:</b> {escape(data['kind'])}\n"
        f"<b>Mazmuni:</b>\n{escape(data['body'])}\n\n"
        f"<b>Holati:</b> Yangi\n"
        f"<b>Vaqti:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )
    sent = await bot.send_message(GROUP_ID, text, reply_markup=status_keyboard(appeal_id))
    if file_id and file_type == "photo":
        await bot.send_photo(GROUP_ID, file_id, caption=f"№{appeal_id:04d} murojaatiga ilova")
    elif file_id and file_type == "document":
        await bot.send_document(GROUP_ID, file_id, caption=f"№{appeal_id:04d} murojaatiga ilova")
    with db() as con:
        con.execute("UPDATE appeals SET group_message_id=? WHERE id=?", (sent.message_id, appeal_id))
    await state.clear()
    await message.answer(
        f"✅ Murojaatingiz qabul qilindi.\n"
        f"Murojaat raqami: <b>№{appeal_id:04d}</b>\n"
        f"Javob va holatni tekshirish uchun ushbu raqamni saqlab qo'ying.",
        reply_markup=main_menu()
    )

@dp.message(F.text == "🔎 Murojaat holatini tekshirish")
async def check_start(message: Message):
    await message.answer("Murojaat raqamini kiriting. Masalan: 0001 yoki 1")

@dp.message(F.text.regexp(r"^\s*№?\s*\d{1,8}\s*$"))
async def check_status(message: Message):
    raw = message.text.replace("№", "").strip()
    appeal_id = int(raw)
    with db() as con:
        row = con.execute(
            "SELECT id, status, created_at, kind FROM appeals WHERE id=? AND user_id=?",
            (appeal_id, message.from_user.id)
        ).fetchone()
    if not row:
        return await message.answer("Bu raqam bo'yicha sizga tegishli murojaat topilmadi.")
    await message.answer(
        f"📄 <b>Murojaat №{row['id']:04d}</b>\n"
        f"Turi: {row['kind']}\nHolati: <b>{row['status']}</b>\n"
        f"Yuborilgan vaqt: {row['created_at']}"
    )

@dp.callback_query(F.data.startswith("st:"))
async def change_status(callback: CallbackQuery):
    _, appeal_id_s, new_status = callback.data.split(":", 2)
    if not await is_group_admin(callback.from_user.id):
        return await callback.answer("Bu amal faqat guruh administratorlari uchun.", show_alert=True)
    appeal_id = int(appeal_id_s)
    with db() as con:
        row = con.execute("SELECT user_id FROM appeals WHERE id=?", (appeal_id,)).fetchone()
        if not row:
            return await callback.answer("Murojaat topilmadi.", show_alert=True)
        con.execute("UPDATE appeals SET status=? WHERE id=?", (new_status, appeal_id))
    await callback.answer("Murojaat holati yangilandi.")
    try:
        await bot.send_message(
            row["user_id"],
            f"📢 Sizning <b>№{appeal_id:04d}</b> murojaatingiz holati "
            f"<b>{new_status}</b> deb yangilandi."
        )
    except Exception:
        pass
    old = callback.message.text or ""
    if "Holati:" in old:
        old = old.rsplit("Holati:", 1)[0] + f"Holati: <b>{new_status}</b>"
    else:
        old += f"\n\nHolati: <b>{new_status}</b>"
    await callback.message.edit_text(old, reply_markup=status_keyboard(appeal_id))

@dp.message(F.text == "ℹ️ Ma'lumot")
async def info(message: Message):
    await message.answer(
        "<b>45-sonli «Nurli maskan» maktab-internati</b>\n"
        "Ushbu bot murojaat, ariza, taklif va shikoyatlarni qabul qilish uchun xizmat qiladi.\n"
        "Murojaat yuborish uchun ism-familiya va telefon raqamini kiritish talab etiladi.",
        reply_markup=main_menu()
    )

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
