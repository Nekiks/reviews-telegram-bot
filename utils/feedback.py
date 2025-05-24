from configs import db_path

from utils.db import db_connect

from utils.teams import get_team_leader_id

import aiogram

import sqlite3

def add_feedback(user_id:int, team_id:int, date:str, content:str, is_anonymous:bool) -> bool:
    conn = db_connect(db_path('feedbacks.db'))    
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO feedbacks (user_id, team_id, content, date, is_closed, is_anonymous) VALUES (?, ?, ?, ?, ?, ?)", (user_id, team_id, content, date, False, is_anonymous))
            feedback_id = cursor.lastrowid 
            conn.commit()
            """Success adding to database"""
            return feedback_id 
        except sqlite3.IntegrityError:
            """If user is not in team"""
            return None
        finally:
            conn.close()

def del_feedback(feedback_id:int) -> bool:
    conn = db_connect(db_path('feedbacks.db'))  
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM feedbacks WHERE feedback_id = ?", (feedback_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f'ERROR: utils/feedback.del_feedback: {e}')
            return False
        finally:
            conn.close()
            return None

def get_all_feedbacks(team_id:int) -> list:
    conn = db_connect(db_path('feedbacks.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM feedbacks WHERE team_id = ?", (team_id,))
    data = cursor.fetchall()
    return data

def get_feedback_data(feedback_id:int):
    conn = db_connect(db_path('feedbacks.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM feedbacks WHERE feedback_id = ?", (feedback_id,))
    data = cursor.fetchone()
    return data

def get_user_id_feedback(feedback_id:int) -> int:
    conn = db_connect(db_path('feedbacks.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM feedbacks WHERE feedback_id = ?", (feedback_id,))
    data = cursor.fetchone()
    return int(data[0])

def notify_about_feedback(bot:aiogram.Bot, team_id:int, content:str):
    leader_id = get_team_leader_id()
    bot.send_message(leader_id, 'Пришло обращение!')

"""
Func main() for testing code
"""
def main():
    #add_feedback(948546, 46456, 'Test', '34 432 2009', 'category')
    print(get_user_id_feedback(1))

if __name__ == "__main__":
    main()
    