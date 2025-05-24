from aiogram import Router, F
from aiogram import types
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup 
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.enums.parse_mode import ParseMode
from handlers.states.team_states import TeamCreationStates, TeamInvitingMembersStates
from aiogram import Bot

from configs import BOT_TOKEN

from utils import add_team_invite_link
from utils import generate_team_inviting_link, get_team_by_invite_hash
from utils import add_team, add_user_at_team, get_team_name
from utils import user_init_start
from utils import check_user_team
from utils import delete_team
from utils import leave_team
from utils import check_user_is_leader
from utils import get_team_users
from utils import get_team_leader_id

router_team = Router()


"""
Team creating
"""
@router_team.message(Command('start'))
async def start(message: types.Message):
    args = message.text.split()
    user = message.from_user
    user_id = message.chat.id
    username = str(user.username)
    name = str(user.first_name)
    last_name = str(user.last_name) 
    user_init_start(user_id, username, name, last_name)
    if len(args) > 1 and args[1].startswith('invite'):
        invite_hash = args[1][7:]
        team_id = get_team_by_invite_hash(invite_hash)
        if not team_id == None:
            if not check_user_is_leader(user_id):
                
                add_user_at_team(user_id, team_id)
                team_name = get_team_name(team_id)
                back_menu_btn = InlineKeyboardButton(text='Вернуться в меню', callback_data='back_menu')
                inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[back_menu_btn]])
                await message.answer(f'Вы вступили в команду <b>{team_name}</b>', parse_mode=ParseMode.HTML, reply_markup=inline_buttons)
            else:
                back_menu_btn = InlineKeyboardButton(text='Вернуться в меню', callback_data='back_menu')
                delete_team_btn = InlineKeyboardButton(text='🗑️ Удалить команду', callback_data='delete_team')
                inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[delete_team_btn], [back_menu_btn]])
                await message.answer('⚠️ Вы лидер команды. \n\nЕсли вы хотите вступить в другую команду, то вам нужно удалить свою', reply_markup=inline_buttons)
        else:
            back_menu_btn = InlineKeyboardButton(text='Вернуться в меню', callback_data='back_menu')
            inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[back_menu_btn]])
            await message.answer('Недействительная ссылка для вступления. \nЗапросите у лидера команды актуальную ссылку', reply_markup=inline_buttons)
    else:
        start_create_team_btn = InlineKeyboardButton(text='Создать команду', callback_data='create_team')
        start_skip_btn = InlineKeyboardButton(text='Пропустить', callback_data='back_menu')
        start_inline_btns = InlineKeyboardMarkup(inline_keyboard=[[start_create_team_btn], [start_skip_btn]])
        await message.answer('Приветствую! \nНачнем с создания команды или вступления в нее.', reply_markup=start_inline_btns)
    

@router_team.callback_query(F.data == 'delete_team')
async def process_delete_team(callback: CallbackQuery):
    confirm_delete_btn = InlineKeyboardButton(text='Удалить группу', callback_data='confirm_delete_team')
    back_team_btn = InlineKeyboardButton(text='Вернуться назад', callback_data='my_team')
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[confirm_delete_btn], [back_team_btn]])
    await callback.message.edit_text('⚠️ <b>ВЫ ДЕЙСТВИТЕЛЬНО ХОТИТЕ УДАЛИТЬ КОМАНДУ?</b> \nДанное действие отменить в дальнейшем будет нельзя', parse_mode=ParseMode.HTML, reply_markup=inline_buttons)

@router_team.callback_query(F.data == 'confirm_delete_team')
async def confirm_delete_team(callback: CallbackQuery):
    user_id = callback.message.chat.id
    back_menu_btn = InlineKeyboardButton(text='Вернуться в меню', callback_data='back_menu')
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[back_menu_btn]])
    
    if check_user_is_leader(user_id):
        team_id = check_user_team(user_id)
        if delete_team(team_id):
            await callback.message.edit_text('Команда успешна удалена!', reply_markup=inline_buttons)
        else:
            await callback.message.edit_text('⚠️Произошла ошибка во время удалении команды', reply_markup=inline_buttons)
    else:
        await callback.message.edit_text('Вы не являетесь лидером текущей команды!', reply_markup=inline_buttons)

@router_team.callback_query(F.data == 'create_team')
async def process_create_team(callback: CallbackQuery, state: FSMContext):
    user_id = callback.message.chat.id
    if check_user_team(user_id) == None:
        await state.set_state(TeamCreationStates.waiting_for_name)
        await callback.message.answer('Введите название команды (1/2): ')
    else:
        await callback.message.answer('Вы уже состоите в команде')

@router_team.message(TeamCreationStates.waiting_for_name)
async def process_team_name(message: types.Message, state: FSMContext):
    await state.update_data(team_name = message.text)
    await state.set_state(TeamCreationStates.waiting_for_desc)
    await message.answer('Введите описание команды (2/2):')

@router_team.message(TeamCreationStates.waiting_for_desc)
async def process_team_desc(message: types.Message, state: FSMContext):
    await state.update_data(team_desc = message.text)
    data = await state.get_data()
    add_team(data['team_name'], data['team_desc'], message.from_user.id)
    bot_info = await message.bot.get_me()
    bot_username = bot_info.username
    user_id = message.chat.id
    team_id = check_user_team(user_id)
    invite_link = generate_team_inviting_link(bot_username, team_id)
    back_menu_btn = InlineKeyboardButton(text='Вернуться в меню', callback_data='back_menu')
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[back_menu_btn]])
    await message.answer(f'Команда создана. \nСсылка для вступления: {invite_link}', reply_markup=inline_buttons)
    await state.clear()

def build_members_keyboard(users: list, leader_id:int, page:int = 0, per_page:int = 10):
    builder = InlineKeyboardBuilder()

    for user in users[page*per_page : (page+1)*per_page]:
        user_id = user[0]
        if user_id != leader_id:
            user_name = user[1]
            user_lastname = user[2] if user[2] != 'None' else ''

            button_text = f'{user_name} {user_lastname}'.strip() if user_lastname else user_name
            builder.button(
                text=button_text,
                callback_data=f'user_team_view_{user_id}'
            )
        else:
            continue
    builder.adjust(2)
    if len(users) > per_page:
        row = []
        if page > 0:
            row.append(InlineKeyboardButton(text='←', callback_data=f'users_team_page_{page-1}'))
        if (page + 1)*per_page < len(users):
            row.append(InlineKeyboardButton(text='→', callback_data=f'users_team_page_{page+1}'))
        builder.row(*row)
    builder.row(InlineKeyboardButton(text='🔙 Вернуться в меню', callback_data='manage_team'))
    return builder

@router_team.callback_query(F.data.startswith('users_team_page_'))
async def users_team_page(callback: CallbackQuery):
    try:
        user_id = callback.message.chat.id
        team_id = check_user_team(user_id)
        users = get_team_users(team_id)
        page = int(callback.data.split('_')[-1])
        builder = build_members_keyboard(users, user_id)
        await callback.message.edit_text(f'Участники команды (Страница {page+1})', reply_markup=builder.as_markup())
    except Exception as e:
        print(f"ERROR: handler.team_handlers.user_team_page: {e}") 
        back_menu_btn = InlineKeyboardButton('Вернуться в меню', callback_data='back_menu')
        inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[back_menu_btn]])
        await callback.message.edit_text('Произошла ошибка при загрузке страницы', reply_markup=inline_buttons)

"""
Manage team
"""
@router_team.callback_query(F.data == 'manage_team')
async def manage_team(callback: CallbackQuery):
    generate_new_link_btn = InlineKeyboardButton(text='Сгенерировать новую инвайт-ссылку', callback_data='generate_new_invite_link')
    team_members_btn = InlineKeyboardButton(text='Участники команды', callback_data='users_team_page_0')
    back_my_team_btn = InlineKeyboardButton(text='Вернуться назад', callback_data='my_team')
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[generate_new_link_btn], [team_members_btn], [back_my_team_btn]])
    await callback.message.edit_text('Управление вашей командой', reply_markup=inline_buttons) 

@router_team.callback_query(F.data == 'generate_new_invite_link')
async def generate_new_invite_link(callback: CallbackQuery):
    bot_info = await callback.message.bot.get_me()
    bot_username = bot_info.username
    user_id = callback.message.chat.id
    team_id = check_user_team(user_id)
    invite_link = generate_team_inviting_link(bot_username, team_id)
    back_manage_team_btn = InlineKeyboardButton(text='Вернуться назад', callback_data='manage_team')
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[back_manage_team_btn]])
    await callback.message.edit_text(f'Новая ссылка для вступления в группу \n{invite_link}', reply_markup=inline_buttons)

"""
Leave team
"""
@router_team.callback_query(F.data == 'leave_team')
async def leave_team_menu(callback: CallbackQuery):
    user_id = callback.message.chat.id
    back_menu_btn = InlineKeyboardButton(text='Вернуться в меню', callback_data='back_menu')
    create_team_btn = InlineKeyboardButton(text='Создать свою команду', callback_data='create_team')
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[create_team_btn], [back_menu_btn]])
    team_id = check_user_team(user_id)
    leave_team(user_id)
    await callback.message.edit_text('✅ Вы вышли из команды', reply_markup=inline_buttons)

"""
Sending invite (NOT WORKING YET)
"""
# @router_team.message(Command('invite'))
# async def proccess_inviting_members(message: types.Message, state: FSMContext):
#     await state.set_state(TeamInvitingMembersStates.waiting_for_username)
#     await message.answer('⚠️ Пользователь, которого вы вводите должен хоть раз зайти в этого бота и прописать /start. Если пользователь менял username, то ему нужно еще раз прописать /start' \
#     '\nВведите username пользователя (@example):')
# @router_team.message(TeamInvitingMembersStates.waiting_for_username)
# async def finish_inviting_members(message: types.Message, state: FSMContext):
#     data = await state.update_data(username = message.text)
#     username = str(message.text).strip()
#     if not username.startswith('@'):
#         retry_btn = InlineKeyboardButton(text='Повторить попытку', callback_data='retry_invite')
#         menu_btn = InlineKeyboardButton(text='Вернуться в меню', callback_data='main_menu')
#         inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[retry_btn], [menu_btn]])
        
#         await message.answer('Введен неверный username! \nПример: @example_username', reply_markup=inline_buttons)
#     else:
#         await message.answer('Успех')

# @router_team.callback_query(F.data == 'retry_invite')
# async def proccess_inviting_members_retry(callback: CallbackQuery, state: FSMContext):
#     await state.set_state(TeamInvitingMembersStates.waiting_for_username)
#     await callback.message.answer('⚠️ Пользователь, которого вы вводите должен хоть раз зайти в этого бота и прописать /start. Если пользователь менял username, то ему нужно еще раз прописать /start' \
#     '\nВведите username пользователя (@example):')
# @router_team.message(TeamInvitingMembersStates.waiting_for_username)
# async def finish_inviting_members_retry(message: types.Message, state: FSMContext):
#     data = await state.update_data(username = message.text)
#     username = str(message.text).strip()
#     if not username.startswith('@'):
#         retry_btn = InlineKeyboardButton(text='Повторить попытку', callback_data='retry_invite')
#         menu_btn = InlineKeyboardButton(text='Вернуться в меню', callback_data='main_menu')
#         inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[retry_btn], [menu_btn]])

#         await message.answer('Введен неверный username! \nПример: @example_username', reply_markup=inline_buttons)
#     else:
#         await message.answer('Успех')


