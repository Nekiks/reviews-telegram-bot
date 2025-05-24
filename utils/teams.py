import sqlite3
from utils.db import db_connect
from configs import db_path
from datetime import date
from aiogram import Bot
from aiogram.utils.deep_linking import create_start_link
import secrets

from configs import BOT_TOKEN
# conn = db_connect(db_path('teams.db'))
# cursor = conn.cursor()

# cursor.execute("""
#         CREATE TABLE IF NOT EXISTS teams (
#             team_id INTEGER PRIMARY KEY,
#             team_name TEXT NOT NULL,
#             team_desc TEXT,
#             leader_id INTEGER NOT NULL,
#             date TEXT NOT NULL,
#             feedbacks_count INTEGER,
#             members_count INTEGER
#         )
#         """)

# conn.commit()
# conn.close()

def add_team(team_name:str, team_desc:str, leader_id:int) -> bool:
    conn = db_connect(db_path('teams.db'))
    cursor = conn.cursor()
    current_date = str(date.today())

    """Предотвращение SQL иньекции"""
    team_data = {
        'team_name': team_name,
        'team_desc': team_desc,
        'leader_id': leader_id,
        'date': current_date
    }

    try:
        cursor.execute("""INSERT INTO teams (team_name, team_desc, leader_id, date) VALUES (:team_name, :team_desc, :leader_id, :date)""", team_data)
        conn.commit()
        team_id = cursor.lastrowid
        conn = db_connect(db_path('users.db'))
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET team_id = ?, is_leader = ? WHERE user_id = ?", (team_id, True, leader_id))

        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

def add_user_at_team(user_id:int, team_id:int) -> bool:
    conn = db_connect(db_path('users.db'))
    cursor = conn.cursor()
    current_date = str(date.today())

    member_data = {
        'user_id': user_id,
        'team_id': team_id,
        'is_leader' : False
    }
    try:
        cursor.execute("UPDATE users SET team_id = ?, is_leader = ? WHERE user_id = ?", (team_id, 0, user_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f'ERROR: utils.teams: {e}')
        conn.close()
        return False

def delete_team(team_id:int) -> bool:
    try:
        conn_users = db_connect(db_path('users.db'))
        cursor = conn_users.cursor()
        cursor.execute("UPDATE users SET team_id = ?, is_leader = ?, is_curator = ? WHERE team_id = ?", (None, 0, 0, team_id))
        conn_users.commit()
        conn_users.close()

        conn_teams = db_connect(db_path('teams.db'))
        cursor = conn_teams.cursor()
        cursor.execute("DELETE FROM teams WHERE team_id = ?", (team_id,))
        conn_teams.commit()
        conn_teams.close()

        conn_feedbacks = db_connect(db_path('feedbacks.db'))
        cursor = conn_feedbacks.cursor()
        cursor.execute("DELETE FROM feedbacks WHERE team_id = ?", (team_id,))
        conn_feedbacks.commit()
        conn_feedbacks.close()
        return True
    except sqlite3.Error as e:
        print(f'ERROR: utils/teams.delete_team: {e}')
        return False 

def leave_team(user_id:int) -> bool:
    try:
        conn = db_connect(db_path('users.db'))
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET team_id = NULL, is_curator = 0 WHERE user_id = ?", (user_id,))
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False

def get_team_name(team_id:int) -> str:
    conn = db_connect(db_path('teams.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT team_name FROM teams WHERE team_id = ?", (team_id,))
    data = cursor.fetchone()
    return data[0]

def get_team_data(team_id:int) -> list:
    conn = db_connect(db_path('teams.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teams WHERE team_id = ?", (team_id,))
    data = cursor.fetchone()
    return data

def get_team_leader_id(team_id:int) -> int:
    conn = db_connect(db_path(db_path('teams.db')))
    cursor = conn.cursor()
    cursor.execute("SELECT leader_id FROM teams WHERE team_id = ?", (team_id,))
    data = cursor.fetchone()
    return data[0]

def add_team_invite_hash(team_id: int, invite_hash: str) -> None:
    conn = db_connect(db_path('teams.db'))
    cursor = conn.cursor()
    cursor.execute("UPDATE teams SET invite_hash = ? WHERE team_id = ?", (invite_hash, team_id))
    conn.commit()

def add_team_invite_link(team_id: int, invite_link: str) -> None:
    conn = db_connect(db_path('teams.db'))
    cursor = conn.cursor()
    cursor.execute("UPDATE teams SET invite_link = ? WHERE team_id = ?", (invite_link, team_id))
    conn.commit()

def get_team_inviting_link(team_id:int) -> str:
    conn = db_connect(db_path('teams.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT invite_link FROM teams WHERE team_id = ?", (team_id,))
    data = cursor.fetchone()
    return data[0]

def get_team_by_invite_hash(invite_hash:str) -> int | None:
    try:
        conn = db_connect(db_path('teams.db'))
        cursor = conn.cursor()
        cursor.execute("SELECT team_id FROM teams WHERE invite_hash = ?", (invite_hash,))
        data = cursor.fetchone()
        return int(data[0])
    except:
        return None

def get_count_team_members(team_id:int) -> int:
    conn = db_connect(db_path('users.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE team_id = ?", (team_id,))
    data = cursor.fetchone()
    return int(data[0])

def generate_team_inviting_link(bot_username:str, team_id:int) -> str:
    invite_hash = f'{secrets.token_urlsafe(16)}'
    invite_link = f"https://t.me/{bot_username}?start=invite_{invite_hash}"
    add_team_invite_link(team_id, invite_link)
    add_team_invite_hash(team_id, invite_hash)
    return invite_link

def get_team_users(team_id:int) -> tuple:
    conn = db_connect(db_path('users.db'))
    cursror = conn.cursor()
    cursror.execute("SELECT user_id, user_name, user_lastname FROM users WHERE team_id = ?", (team_id,))
    data = cursror.fetchall()
    return data

"""Testing code"""
if __name__ == '__main__':
    # add_team('name', 'desc', 435453465345)
    # check_user_team(830401599)
    # add_team_invite_link(2, 'test')
    pass