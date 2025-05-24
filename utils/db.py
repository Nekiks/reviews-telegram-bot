import sqlite3
from sqlite3 import Error

from configs.config_db import db_path

def db_connect(db_path:str) -> sqlite3.connect:
    connect = None 
    try:
        connect = sqlite3.connect(db_path)
        return connect
    except Error as e:
        print(f'\nERROR: in utils.db_utils.db_connect (db: {db_path}): {e}\n')
    return connect

def db_all_init() -> None:
    try:
        conn = sqlite3.connect(db_path('users.db'))
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username INTEGER NOT NULL,
            team_id INTEGER DEFAULT NULL,
            is_leader BOOLEAN DEFAULT 0,
            is_curator BOOLEAN DEFAULT 0,
            feedbacks_count INTEGER DEFAULT 0,
            reg_date TEXT,
            user_name TEXT,
            user_lastname TEXT,
            is_admin BOOLEAN DEFAULT 0
        )
        """)
        
        conn = sqlite3.connect(db_path('feedbacks.db'))
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedbacks (
            feedback_id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            team_id INTEGER DEFAULT NULL,
            date TEXT NOT NULL,
            category TEXT DEFAULT NULL,
            content TEXT NOT NULL,
            is_closed BOOLEAN DEFAULT 0,
            is_anonymous BOOLEAN DEFAULT 0
        )
        """)

        conn = sqlite3.connect(db_path('teams.db'))
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            team_id INTEGER PRIMARY KEY,
            team_name TEXT NOT NULL,
            team_desc TEXT DEFAULT 'Описания нет',
            leader_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            feedbacks_count INTEGER DEFAULT 0,
            members_count INTEGER DEFAULT 1,
            invite_link TEXT,
            invite_hash TEXT
        )
        """)

    except Exception as e:
        print(f'ERROR: utils.db.db_init: {e}')

    
    