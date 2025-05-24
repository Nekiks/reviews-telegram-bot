from aiogram import Router, F
from aiogram import types
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.enums.parse_mode import ParseMode
from handlers.states.team_states import TeamCreationStates, TeamInvitingMembersStates

from configs import db_path
from utils import db_connect
from utils import add_team
from utils import user_init_start, get_username
from utils import check_user_team
from utils import check_user_is_leader, check_user_is_admin, get_team_data
from utils import get_all_feedbacks
from utils import generate_team_inviting_link
from utils import get_team_inviting_link
from utils import get_feedbacks_count_user
from utils import get_reg_date_user
from utils import get_count_team_members

router_menu = Router()

"""
Main menu
"""
@router_menu.message(Command('menu'))
async def menu_main(message: types.Message):
    user_id = message.chat.id
    send_feedback_btn = InlineKeyboardButton(text='Создать обратную связь', callback_data='send_feedback')
    manage_feedbacks_btn = InlineKeyboardButton(text='Перейти к обращениям', callback_data='manage_feedbacks')
    my_team_btn = InlineKeyboardButton(text='Моя команда', callback_data='my_team')
    my_account_btn = InlineKeyboardButton(text='Аккаунт', callback_data='my_account')
    admin_panel_btn = InlineKeyboardButton(text='Панель администратора', callback_data='admin_panel')
    if check_user_is_leader(user_id):
        if check_user_is_admin(user_id):
            inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[manage_feedbacks_btn], [send_feedback_btn], [my_team_btn, my_account_btn], [admin_panel_btn]])
        else:
            inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[manage_feedbacks_btn], [send_feedback_btn], [my_team_btn, my_account_btn]])
    else:
        if check_user_is_admin(user_id):
            inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[send_feedback_btn], [my_team_btn, my_account_btn], [admin_panel_btn]])
        else:
            inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[send_feedback_btn], [my_team_btn, my_account_btn]])
    name = message.chat.first_name
    await message.answer(
        f'Приветствую, {name}!'
        f'\n\n⚠️ <em>Многие функции недоступны и не видны обычным участникам команды</em>',
        parse_mode=ParseMode.HTML,
        reply_markup=inline_buttons
    )
@router_menu.callback_query(F.data == 'back_menu')
async def back_menu_main(callback: types.CallbackQuery):
    user_id = callback.message.chat.id
    send_feedback_btn = InlineKeyboardButton(text='Создать обращение', callback_data='send_feedback')
    manage_feedbacks_btn = InlineKeyboardButton(text='Перейти к обращениям', callback_data='manage_feedbacks')
    my_team_btn = InlineKeyboardButton(text='Моя команда', callback_data='my_team')
    my_account_btn = InlineKeyboardButton(text='Профиль', callback_data='my_profile')
    admin_panel_btn = InlineKeyboardButton(text='Панель администратора', callback_data='admin_panel')
    if not check_user_is_leader(user_id):
        if not check_user_is_admin(user_id):
            inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[send_feedback_btn], [my_team_btn, my_account_btn]])
        else:
            inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[send_feedback_btn], [my_team_btn, my_account_btn], [admin_panel_btn]])
    else:
        if not check_user_is_admin(user_id):
            inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[manage_feedbacks_btn], [send_feedback_btn], [my_team_btn, my_account_btn]])
        else:
            inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[manage_feedbacks_btn], [send_feedback_btn], [my_team_btn, my_account_btn], [admin_panel_btn]])
    name = callback.message.chat.first_name
    await callback.message.edit_text(
        f'Приветствую, {name}!'
        f'\n\n⚠️ <em>Многие функции недоступны и не видны обычным участникам команды</em>',
        parse_mode=ParseMode.HTML,
        reply_markup=inline_buttons
    )

"""
Profile menu
"""
@router_menu.callback_query(F.data == 'my_profile')
async def my_profile_menu(callback: types.CallbackQuery):
    user_id = callback.message.chat.id
    user_name = callback.message.chat.first_name
    reg_date_temp = get_reg_date_user(user_id)
    reg_date = ''
    for el in reg_date_temp:
        if el != '-':
            reg_date += el
        else:
            reg_date += '.'
    feedbacks_count = get_feedbacks_count_user(user_id)
    back_menu_btn = InlineKeyboardButton(text='Вернуться в меню', callback_data='back_menu')
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[back_menu_btn]])
    await callback.message.edit_text(
        f'Последнее известное имя: {user_name}'
        f'\nДата регистрации: {reg_date}'
        f'\nКоличество актуальных обращений: {feedbacks_count}',
        reply_markup=inline_buttons
    )

    
"""
Team menu
"""
@router_menu.callback_query(F.data == 'my_team')
async def menu_team(callback: types.CallbackQuery):
    user_id = callback.message.chat.id
    if check_user_team(user_id) == None:
        create_team_btn = InlineKeyboardButton(text='Создать команду', callback_data='create_team')
        back_menu_btn = InlineKeyboardButton(text='Вернуться в меню', callback_data='back_menu')
        inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[create_team_btn], [back_menu_btn]])
        await callback.message.edit_text('⚠️ У вас нет команды. \n\nЗапросите приглашение у лидера или создайте свою', reply_markup=inline_buttons)
    else:
        team_id = check_user_team(user_id)
        data = get_team_data(team_id)
        manage_btn = InlineKeyboardButton(text='Управление командой', callback_data='manage_team')
        feedbacks_list_btn = InlineKeyboardButton(text='Перейти к обращениям', callback_data='manage_feedbacks') ## Дописать
        send_feedback_btn = InlineKeyboardButton(text = 'Создать обратную связь', callback_data='back_menu') ## Дописать
        back_menu_btn = InlineKeyboardButton(text='Вернуться в меню', callback_data='back_menu')
        get_invite_link_btn = InlineKeyboardButton(text='Ссылка для приглашения',callback_data='get_invite_link')
        delete_team_btn = InlineKeyboardButton(text='🗑️ Удалить команду', callback_data='delete_team')
        leave_team_btn = InlineKeyboardButton(text='🔙 Выйти из команды', callback_data='leave_team')
        if check_user_is_leader(user_id):
            inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[manage_btn], [get_invite_link_btn], [delete_team_btn], [back_menu_btn]])
            await callback.message.edit_text(
                f'Айди вашей команды: {data[0]}'
                f'\nКоличество участников: {get_count_team_members(team_id)}'
                f'\nАйди лидера: {data[3]} (Вы)' 
                f'\nДата создания: {data[4]}' 
                f'\n\nИмя команды: {data[1]}'
                f'\nОписание: {data[2]}',
                reply_markup=inline_buttons,
                parse_mode=ParseMode.HTML
            )
        else:
            inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[send_feedback_btn],[leave_team_btn], [back_menu_btn]])
            await callback.message.edit_text(
                f'Айди вашей команды: {data[0]}'
                f'\nАйди лидера: {data[3]} (@{get_username(data[3])})' 
                f'\nДата создания: {data[4]}' 
                f'\n\nИмя команды: {data[1]}'
                f'\nОписание: {data[2]}'
                f'\n\n⚠️ <em>Многие функции недоступны и не видны обычным участникам команды</em>', 
                reply_markup=inline_buttons,
                parse_mode=ParseMode.HTML
            )

@router_menu.callback_query(F.data == 'get_invite_link')
async def get_invite_link(callback: types.CallbackQuery):
    user_id = callback.message.chat.id
    team_id = check_user_team(user_id)
    invite_link = get_team_inviting_link(team_id)
    back_btn = InlineKeyboardButton(text='Вернуться назад', callback_data='my_team')
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[back_btn]])
    await callback.message.edit_text(f'Ссылка для вступления в вашу команду: \n{invite_link}', reply_markup=inline_buttons)


"""
Manage feedback
"""
# @router_menu.callback_query(F.data == 'manage_feedbacks')
# async def manage_feedbacks(callback: types.CallbackQuery):
#     pass

def build_feedbacks_keyboard(feedbacks:list, page:int = 0, per_page:int = 5) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    for feedback in feedbacks[page*per_page : (page+1)*per_page]:
        feedback_id = feedback[0]
        feedback_content = str(feedback[5])
        builder.button(
            text=f"📝 {feedback_content[:15]}..." if len(feedback_content) > 15 else f"📝 {feedback_content}",
            callback_data=f"view_feedback_{feedback_id}"
        )
    builder.adjust(2)
    
    if len(feedbacks) > per_page:
        row = []
        if page > 0:
            row.append(InlineKeyboardButton(text='←', callback_data=f'feedback_page_{page-1}'))
        if (page+1)*per_page < len(feedbacks):
            row.append(InlineKeyboardButton(text='→', callback_data=f'feedback_page_{page+1}'))
        builder.row(*row)
    
    builder.row(InlineKeyboardButton(text='Вернуться в меню', callback_data='back_menu'))
    return builder

@router_menu.callback_query(F.data == 'manage_feedbacks')
async def show_feedbacks_page(callback: CallbackQuery):
    user_id = callback.message.chat.id
    team_id = check_user_team(user_id)
    feedbacks = get_all_feedbacks(team_id)
    if not feedbacks:
        back_menu_btn = InlineKeyboardButton(text='Вернуться в меню', callback_data='back_menu')
        inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[back_menu_btn]])
        await callback.message.edit_text('Сообщений в команде нет', reply_markup=inline_buttons)
        return
    
    builder = build_feedbacks_keyboard(feedbacks, page=0)

    await callback.message.edit_text('Список обращений:', reply_markup=builder.as_markup())

@router_menu.callback_query(F.data.startswith('feedback_page_'))
async def feedback_page(callback: CallbackQuery):
    try:
        page = int(callback.data.split('_')[-1])
        user_id = callback.message.chat.id
        team_id = check_user_team(user_id)
        
        feedbacks = get_all_feedbacks(team_id)
        builder = build_feedbacks_keyboard(feedbacks, page)
        await callback.message.edit_text(f'Список обращений (Страница {page+1}):', reply_markup=builder.as_markup())
    except Exception as e:
        print(f"Error: {e}") 
        back_menu_btn = InlineKeyboardButton('Вернуться в меню', callback_data='back_menu')
        inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[back_menu_btn]])
        await callback.message.edit_text('Произошла ошибка при загрузке страницы', reply_markup=inline_buttons)

@router_menu.callback_query(F.data.startswith('view_feedback_'))
async def view_feedback(callback: CallbackQuery):
    feedback_id = int(callback.data.split('_')[-1])
    conn = db_connect(db_path('feedbacks.db'))
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM feedbacks WHERE feedback_id = ?', (feedback_id,))
    feedback = cursor.fetchone()

    if not feedback:
        await callback.answer('⚠️ Обращение не найдено', show_alert=True)
        return
    answer_btn = InlineKeyboardButton(text='Ответить', callback_data=f'answer_feedback_{feedback_id}')
    delete_feedback_btn = InlineKeyboardButton(text='Удалить', callback_data=f'delete_feedback_{feedback_id}')
    back_feedbacks_btn = InlineKeyboardButton(text='Вернуться назад', callback_data='feedback_page_0')
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[answer_btn, delete_feedback_btn], [back_feedbacks_btn]])
    if feedback[7] == True:
        author_username = 'Анонимно'
    else:
        author_username = f'@{get_username(feedback[1])}'
    await callback.message.edit_text(
        f'Обращение №{feedback[0]}'
        f'\nАвтор обращения: {author_username}'
        f'\nДата: {feedback[3]}'
        f'\nСодержание: \n<pre>{feedback[5]}</pre>',
        reply_markup=inline_buttons,
        parse_mode=ParseMode.HTML
    )

"""
Admin panel
"""
@router_menu.callback_query(F.data == 'admin_panel')
async def admin_panel(callback: CallbackQuery):
    user_id = callback.message.chat.id
    if check_user_is_admin(user_id):
        get_database_btn = InlineKeyboardButton(text='Получить базу данных', callback_data='get_database')
        teams_category = InlineKeyboardButton(text='Управлять командами', callback_data='admin_team_category')
        back_menu_btn = InlineKeyboardButton(text='Вернуться назад', callback_data='back_menu')
        inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[get_database_btn], [teams_category], [back_menu_btn]])
        await callback.message.edit_text('Панель администратора:', reply_markup=inline_buttons)
    else:
        back_menu_btn = InlineKeyboardButton(text='Вернуться назад', callback_data='back_menu')
        inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[back_menu_btn]])
        await callback.message.edit_text('Вы не администратор', reply_markup=inline_buttons)

@router_menu.callback_query(F.data == 'back_admin_panel')
async def back_admin_panel(callback: CallbackQuery):
    user_id = callback.message.chat.id
    if check_user_is_admin(user_id):
        get_database_btn = InlineKeyboardButton(text='Получить базу данных', callback_data='get_database')
        back_menu_btn = InlineKeyboardButton(text='Вернуться назад', callback_data='back_menu')
        inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[get_database_btn], [back_menu_btn]])
        await callback.message.answer('Панель администратора:', reply_markup=inline_buttons)
    else:
        back_menu_btn = InlineKeyboardButton(text='Вернуться назад', callback_data='back_menu')
        inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[back_menu_btn]])
        await callback.message.answer('Вы не администратор', reply_markup=inline_buttons)

@router_menu.callback_query(F.data == 'admin_team_category')
async def admin_team_category(callback: CallbackQuery):
    user_id = callback.message.chat.id
    if check_user_is_admin(user_id):
        back_admin_panel_btn = InlineKeyboardButton(text='Вернться назад', callback_data='admin_panel')
        delete_team_btn = InlineKeyboardButton(text='Удалить команду по ID', callback_data='admin_delete_team')
        inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[delete_team_btn], [back_admin_panel_btn]])
        await callback.message.edit_text('Управление командами', reply_markup=inline_buttons)
    else:
        back_menu_btn = InlineKeyboardButton(text='Вернуться назад', callback_data='back_menu')
        inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[back_menu_btn]])
        await callback.message.answer('Вы не администратор', reply_markup=inline_buttons)