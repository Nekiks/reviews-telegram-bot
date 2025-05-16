import sqlite3
from utils.db_utils import db_connect
from configs import db_path

def get_user_id_username(username:str) -> int:
    conn = db_connect(db_path('users.db'))
def get_username(user_id:int) -> str:
    conn = db_connect(db_path('users.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
    data = cursor.fetchone()
    return data[0]

def check_user_team(user_id: int) -> str | None:
    conn = db_connect(db_path('users.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT team_id FROM users WHERE user_id = ?", (user_id,))
    data = cursor.fetchone()
    if data and data[0] is not None: 
        conn.close()
        return data[0]
    else:
        conn.close()
        return None

def check_user_is_leader(user_id:int) -> bool:
    conn = db_connect(db_path('users.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT is_leader FROM users WHERE user_id = ?", (user_id,))
    data = cursor.fetchone()
    if data[0] == 1:
        return True
    else:
        return False

def check_user_is_admin(user_id:int) -> bool:
    conn = db_connect(db_path('users.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT is_admin FROM users WHERE user_id = ?", (user_id,))
    data = cursor.fetchone()
    if data[0] == 1:
        return True
    else:
        return False

if __name__ == '__main__':
    check_user_is_leader(830401599)