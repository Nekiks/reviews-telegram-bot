from handlers.team_handlers import router_team
from handlers.menu_handlers import router_menu
from handlers.feedback_handler import router_feedback

routers = [
    router_team,
    router_menu,
    router_feedback
]