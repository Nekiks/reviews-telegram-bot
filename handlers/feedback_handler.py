from aiogram import Router, F
from aiogram import Bot
from aiogram import types
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup 
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.enums.parse_mode import ParseMode
from handlers.states.team_states import TeamCreationStates, TeamInvitingMembersStates
from handlers.states.feedback_states import AnswerFeedbackStates
from handlers.states import FeedbackStates
from datetime import date

from configs import BOT_TOKEN

from utils import get_username
from utils import check_user_team
from utils import add_feedback, del_feedback, get_user_id_feedback, get_feedback_data
from utils import get_team_by_invite_hash
from utils import notify_about_feedback
from utils import get_team_leader_id

router_feedback = Router()

@router_feedback.callback_query(F.data == 'cancel_feedback_form')
async def cancel_feedback_form(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    back_menu = InlineKeyboardButton(text='Вернуться в меню', callback_data='back_menu')
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[back_menu]])
    await callback.message.edit_text('Заполнение обращения отменено', reply_markup=inline_keyboard)
    await callback.answer()


@router_feedback.callback_query(F.data == 'send_feedback')
async def process_send_feedback(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.message.chat.id
    if not check_user_team(user_id) == None:
        named_btn = InlineKeyboardButton(text='Анонимно', callback_data='send_feedback_unnamed')
        unnamed_btn = InlineKeyboardButton(text='Не анонимно', callback_data='send_feedback_named')
        cancel_btn = InlineKeyboardButton(text='Отмена', callback_data='cancel_feedback_form')
        inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[named_btn, unnamed_btn], [cancel_btn]])
        await callback.message.edit_text('Как будете отправлять обращение?', reply_markup=inline_buttons)
    else:
        create_team_btn = InlineKeyboardButton(text='Создать команду', callback_data='create_team')
        back_menu_btn = InlineKeyboardButton(text='Вернуться в меню', callback_data='back_menu')
        inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[create_team_btn], [back_menu_btn]])
        await callback.message.edit_text('У вас нет команды. Запросите приглащение у лидера или создайте свою', reply_markup=inline_buttons)

@router_feedback.callback_query(F.data == ('send_feedback_unnamed'))
async def process_send_feedback_unnamed(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(is_anonymous = True)
    await state.set_state(FeedbackStates.waiting_for_content)
    cancel_btn = InlineKeyboardButton(text='Отмена', callback_data='cancel_feedback_form')
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[cancel_btn]])
    await callback.message.answer('Введите обращение:', reply_markup=inline_buttons)

@router_feedback.callback_query(F.data == ('send_feedback_named'))
async def process_send_feedback_named(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(is_anonymous = False)
    await state.set_state(FeedbackStates.waiting_for_content)
    cancel_btn = InlineKeyboardButton(text='Отмена', callback_data='cancel_feedback_form')
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[cancel_btn]])
    await callback.message.answer('Введите обращение:', reply_markup=inline_buttons)


@router_feedback.message(FeedbackStates.waiting_for_content)
async def finish_send_feedback(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    team_id = check_user_team(user_id)
    current_date = date.today()

    await state.update_data(content = message.text)
    data = await state.get_data()
    feedback_id = add_feedback(user_id, team_id, current_date, data['content'], data['is_anonymous'])
    back_menu = InlineKeyboardButton(text='Вернуться в меню', callback_data='back_menu')
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[back_menu]])
    await message.answer('Обращение отправлено лидеру и кураторам', reply_markup=inline_buttons)
    bot = Bot(token=BOT_TOKEN)
    leader_id = get_team_leader_id(team_id)
    
    open_feedback_btn = InlineKeyboardButton(text='Открыть обращение',callback_data=f'view_feedback_{feedback_id}')
    answer_feedback_btn = InlineKeyboardButton(text='Ответить', callback_data=f'answer_feedback_{feedback_id}')
    delete_feedback_btn = InlineKeyboardButton(text='Удалить', callback_data=f'delete_feedback_{feedback_id}')
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[open_feedback_btn], [answer_feedback_btn], [delete_feedback_btn]])
    await bot.send_message(
        leader_id, 
        f'📥 Пришло новое обращение!\n <pre>{data['content']}</pre>',
        parse_mode=ParseMode.HTML,
        reply_markup=inline_buttons
    )
    await bot.session.close()
    await state.clear()

@router_feedback.callback_query(F.data.startswith('delete_feedback_'))
async def delete_feedback(callback: CallbackQuery):
    feeedback_id = int(callback.data.split('_')[-1])
    back_feedback_page_btn = InlineKeyboardButton(text='Вернуться назад', callback_data='feedback_page_0')
    back_menu_btn = InlineKeyboardButton(text='Вернуться в меню', callback_data='back_menu')
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[back_feedback_page_btn], [back_menu_btn]])
    try:
        await callback.message.edit_text('✅ Вы удалили обращение', reply_markup=inline_buttons)
        del_feedback(feeedback_id)
    except Exception as e:
        print('ERROR: handlers/feedback_handler.delete_feedback')
        await callback.message.answer('⚠️', InlineKeyboardButton)

@router_feedback.callback_query(F.data.startswith('answer_feedback_'))
async def process_answer_feedback(callback: CallbackQuery, state: FSMContext):
    feedback_id = int(callback.data.split('_')[-1])
    await state.update_data(feedback_id = feedback_id)
    await state.set_state(AnswerFeedbackStates.waiting_for_answer)
    await callback.message.answer('Введите сообщение, которое будет отправлено автору обращения:')
@router_feedback.message(AnswerFeedbackStates.waiting_for_answer)
async def finish_answer_feedback(message: types.Message, state: FSMContext):
    await state.update_data(answer = message.text)
    delete_feedback_btn = InlineKeyboardButton(text='Удалить обращение', callback_data='delete_feedback_')
    back_feedbacks_btn = InlineKeyboardButton(text='Вернуться назад', callback_data='feedback_page_0')
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[delete_feedback_btn], [back_feedbacks_btn]])
    await message.answer('Отправили ваш ответ', reply_markup=inline_buttons)

    data = await state.get_data()
    feedback_data = get_feedback_data(data['feedback_id'])
    user_id = feedback_data[1]
    feedback_content = feedback_data[5]
    feedback_date = feedback_data[3]
    curator_username = get_username(feedback_data[1])
    answer = data['answer']
    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.send_message(user_id, f'✉️ Вам ответил @{curator_username} \nДата обращения: {feedback_date} \nВаше обращение: <pre>{feedback_content}</pre> \nОтвет: <pre>{answer}</pre>', parse_mode=ParseMode.HTML)
    except Exception as e:
        print(f'ERROR: handler/feedback_handler.finish_answer_feedback: {e}')
        back_feedback = InlineKeyboardButton('Вернуться назад', callback_data='feedback_page_0')
        inline_buttons = InlineKeyboardMarkup(inline_keyboard=[[back_feedback]])
        await message.answer('⚠️ Произошла ошибка при отправке ответа', reply_markup=inline_buttons)
    finally:
        await bot.session.close()

