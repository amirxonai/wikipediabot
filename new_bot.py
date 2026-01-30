import logging
import asyncio
import wikipedia
from aiogram import Bot,Dispatcher,types,F
from aiogram.filters import CommandStart
import os
from dotenv import load_dotenv

wikipedia.set_lang("uz")
load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token = API_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.reply(
        "Xush kelibsiz. Wikipedia - malumotlarni izlash boti"
    )

@dp.message(F.text)
async def wiki_handler(message: types.Message):
    try:
        response = wikipedia.summary(message.text, sentences = 4)
        await message.answer(response)
    except Exception:
        await message.answer("Ma'lumot topilmadi")

        
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())