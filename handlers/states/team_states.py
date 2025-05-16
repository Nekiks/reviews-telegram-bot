from aiogram.fsm.state import State, StatesGroup

class TeamCreationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_desc = State()

class TeamInvitingMembersStates(StatesGroup):
    waiting_for_username = State()