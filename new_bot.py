import logging
import asyncio
import wikipedia
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Default language
DEFAULT_LANG = "uz"
user_langs = {}

def get_user_lang(user_id):
    return user_langs.get(user_id, DEFAULT_LANG)

@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.reply(
        "Xush kelibsiz! Wikipedia botiga.\n"
        "Tilni o'zgartirish uchun /lang buyrug'ini bosing.\n"
        "Qidirish uchun matn yuboring."
    )

@dp.message(Command("help"))
async def send_help(message: types.Message):
    await message.reply(
        "/start - Botni ishga tushirish\n"
        "/help - Yordam\n"
        "/lang - Tilni o'zgartirish (uz, ru, en)\n"
        "Biron bir mavzu yozing, men u haqida ma'lumot beraman."
    )

@dp.message(Command("lang"))
async def change_language(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
    ])
    await message.reply("Tilni tanlang / Choose functionality:", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery):
    lang_code = callback.data.split("_")[1]
    user_langs[callback.from_user.id] = lang_code
    
    responses = {
        "uz": "Til o'zgartirildi: O'zbek",
        "ru": "Язык изменен: Русский",
        "en": "Language changed: English"
    }
    
    await callback.message.answer(responses.get(lang_code, "OK"))
    await callback.answer()

@dp.message(F.text)
async def wiki_handler(message: types.Message):
    lang = get_user_lang(message.from_user.id)
    wikipedia.set_lang(lang)
    
    try:
        data = wikipedia.page(message.text)
        summary = wikipedia.summary(message.text, sentences=5)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="To'liq o'qish", url=data.url)]
        ])
        
        await message.answer(summary, reply_markup=keyboard)
        
    except wikipedia.exceptions.DisambiguationError as e:
        options = e.options[:5] # Limit to 5 options
        buttons = []
        for option in options:
            buttons.append([InlineKeyboardButton(text=option, callback_data=f"search_{option[:20]}")]) # Limit callback data length
            
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer("Bir nechta ma'lumot topildi. Qaysi birini nazarda tutdingiz?", reply_markup=keyboard)
        
    except wikipedia.exceptions.PageError:
        msg = {
            "uz": "Ma'lumot topilmadi.",
            "ru": "Информация не найдена.",
            "en": "Information not found."
        }
        await message.answer(msg.get(lang, msg["uz"]))
    except Exception as e:
        logging.error(e)
        await message.answer("Xatolik yuz berdi / Error occurred")

@dp.callback_query(F.data.startswith("search_"))
async def search_from_button(callback: CallbackQuery):
    query = callback.data.split("search_")[1]
    # Call the wiki handler logic again, but we can't directly call the message handler easily without mocking.
    # So we'll just replicate logic or call a helper.
    # For now, let's just use wikipedia.page directly here to show we can.
    
    lang = get_user_lang(callback.from_user.id)
    wikipedia.set_lang(lang)
    
    try:
        summary = wikipedia.summary(query, sentences=5)
        # We need the URL too, so maybe .page is better, but .page might raise disambiguation again if query is still vague?
        # Usually selecting from options is specific enough.
        page = wikipedia.page(query)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Link", url=page.url)]
        ])
        
        await callback.message.answer(summary, reply_markup=keyboard)
    except Exception as e:
        await callback.message.answer("Xatolik / Error")
        
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
