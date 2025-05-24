from aiogram.fsm.state import State, StatesGroup

class DeleteTeamState(StatesGroup):
    waiting_for_team_id = State()