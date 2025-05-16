from aiogram.fsm.state import State, StatesGroup

class FeedbackStates(StatesGroup):
    waiting_for_unnamed = State()
    waiting_for_content = State()

class AnswerFeedbackStates(StatesGroup):
    waiting_for_answer = State()