from handlers.team_handlers import router_team
from handlers.menu_handlers import router_menu
from handlers.feedback_handler import router_feedback
from handlers.admin_handlers import router_admin

routers = [
    router_team,
    router_menu,
    router_feedback,
    router_admin
]