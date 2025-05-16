from aiogram import Bot
from configs import BOT_TOKEN   

def get_bot_username() -> str:
    bot = Bot(token=BOT_TOKEN)