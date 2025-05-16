"""
User init. at first joining to the bot (init. user by the '/start' command)
"""
from sqlite3 import Error

from utils.db_utils import db_connect
from configs import db_path
from datetime import date

def user_init_start(user_id:int, username:str, user_name:str, user_lastname: str) -> None:
    conn = db_connect(db_path('users.db'))
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        exists = cursor.fetchone()
        if exists:
            cursor.execute("UPDATE users SET username = ?, user_name = ?, user_lastname = ? WHERE user_id = ?", (username, user_name, user_lastname, user_id))
        else:
            current_date = str(date.today())
            cursor.execute("""INSERT INTO users (user_id, username, reg_date, user_name, user_lastname) VALUES (?, ?, ?, ?, ?)""", (user_id, username, current_date, user_name, user_lastname))
        conn.commit()
    except Error as e:
        print(f'ERROR: utils.join_init: {e}')
    finally:
        conn.close()

if __name__ == '__main__':
    user_init_start(345345, 'testing', 'Name')
    