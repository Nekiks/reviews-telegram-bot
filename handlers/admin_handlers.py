from aiogram import Router, F
from aiogram import Bot
from aiogram import types
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup 
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.enums.parse_mode import ParseMode
from datetime import date

from configs import BOT_TOKEN

from utils import get_username
from utils import check_user_team
from utils import add_feedback, del_feedback, get_user_id_feedback, get_feedback_data
from utils import get_team_by_invite_hash
from utils import create_db_json
from utils import delete_team
from utils import check_user_is_admin

from handlers.states import DeleteTeamState

router_admin = Router()

@router_admin.callback_query(F.data == 'get_database')
async def get_database(callback: CallbackQuery):
    users_db_btn = InlineKeyboardButton(text='Пользователи', callback_data='get_database_users')
    teams_db_btn = InlineKeyboardButton(text='Команды', callback_data='get_database_teams')
    feedbacks_db_btn = InlineKeyboardButton(text='Обращения', callback_data='get_database_feedbacks')
    back_admin_btn = InlineKeyboardButton(text='Вернуться назад', callback_data='admin_panel')
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[users_db_btn], [teams_db_btn], [feedbacks_db_btn], [back_admin_btn]])

    await callback.message.edit_text('Выберите базу данных', reply_markup=inline_buttons)

@router_admin.callback_query(F.data == 'get_database_users')
async def get_database_users(callback: CallbackQuery):
    path = create_db_json('users.db')
    back_admin_btn = InlineKeyboardButton(text='Вернуться назад', callback_data='back_admin_panel')
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[back_admin_btn]])
    await callback.message.answer_document(document=types.FSInputFile(path), caption='База данных с пользователями', reply_markup=inline_buttons)

@router_admin.callback_query(F.data == 'get_database_teams')
async def get_database_users(callback: CallbackQuery):
    path = create_db_json('teams.db')
    back_admin_btn = InlineKeyboardButton(text='Вернуться назад', callback_data='back_admin_panel')
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[back_admin_btn]])
    await callback.message.answer_document(document=types.FSInputFile(path), caption='База данных с пользователями', reply_markup=inline_buttons)

@router_admin.callback_query(F.data == 'get_database_feedbacks')
async def get_database_users(callback: CallbackQuery):
    path = create_db_json('feedbacks.db')
    back_admin_btn = InlineKeyboardButton(text='Вернуться назад', callback_data='back_admin_panel')
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[back_admin_btn]])
    await callback.message.answer_document(document=types.FSInputFile(path), caption='База данных с пользователями', reply_markup=inline_buttons)
    



@router_admin.callback_query(F.data == 'admin_delete_team')
async def admin_delete_team(callback: CallbackQuery, state: FSMContext):
    user_id = callback.message.chat.id
    if check_user_is_admin(user_id):
        cancel_btn = InlineKeyboardButton(text='Отмена', callback_data='admin_cancel_delete_team')
        inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[cancel_btn]])
        await callback.message.edit_text('Введите ID команды:', reply_markup=inline_buttons)
        await state.set_state(DeleteTeamState.waiting_for_team_id)
    else:
        back_menu_btn = InlineKeyboardButton(text='Вернуться назад', callback_data='back_menu')
        inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[back_menu_btn]])
        await callback.message.answer('Вы не администратор', reply_markup=inline_buttons)

@router_admin.message(DeleteTeamState.waiting_for_team_id)
async def admin_delete_team_finish(message: Message, state: FSMContext):
    user_id = message.chat.id
    if check_user_is_admin(user_id):
        await state.update_data(team_id = message.text)
        data = await state.get_data()
        back_admin_team_btn = InlineKeyboardButton(text='Вернуться назад', callback_data='admin_team_category')
        inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[back_admin_team_btn]])
        try:
            delete_team(data['team_id'])
            await message.answer(f'Команда {data['team_id']} удалена, если она существовала', reply_markup=inline_buttons)
            await state.clear()
        except:
            await message.answer('Произошла ошибка. Проверьте введенный ID команды', reply_markup=inline_buttons)
            await state.clear()
    else:
        back_menu_btn = InlineKeyboardButton(text='Вернуться назад', callback_data='back_menu')
        inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[back_menu_btn]])
        await message.answer('Вы не администратор', reply_markup=inline_buttons)