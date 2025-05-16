from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
from aiogram import types, F
from aiogram.fsm.context import FSMContext 
from aiogram import Router
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from handlers import routers
from configs import BOT_TOKEN


bot = Bot(token=BOT_TOKEN)
# router = Router()
dp = Dispatcher()
# dp.include_router(router)


# start_create_team_btn = InlineKe''']yboardButton(text='Создать команду', callback_data='create')
# start_skip_btn = InlineKeyboardButton(text='Пропустить', callback_data='skip')
# start_inline_btns = InlineKeyboardMarkup(inline_keyboard=[[start_create_team_btn], [start_skip_btn]])
# @router.message(Command('start'))
# async def start(message: types.Message):
#     await message.answer('Приветствую! \nНачнем с создания команды или вступления в нее.', reply_markup=start_inline_btns)


for router in routers:
        dp.include_router(router)

async def main():
    await dp.start_polling(bot)
    

if __name__ == "__main__":
    asyncio.run(main())
    