from aiogram import Bot, Dispatcher, Router
from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
import asyncio

"""Project packages"""
from configs import BOT_TOKEN
from handlers import routers
from utils import db_all_init

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

for router in routers:
        dp.include_router(router)

async def main():
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    db_all_init()
    asyncio.run(main())
    
