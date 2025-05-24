import sqlite3
from utils.db import db_connect
from configs import db_path
from datetime import date
from aiogram import Bot
from aiogram.utils.deep_linking import create_start_link
import secrets
import pandas as pd

from configs import BOT_TOKEN

def create_db_json(db_name) -> str:
    conn = db_connect(db_path(db_name))
    dataframe = pd.read_sql_query(f"SELECT * FROM {db_name[:-3]}", conn)
    dataframe.to_json(f"databases_json/{db_name}.json", orient="records", indent=4)  # или to_json
    conn.close()
    return f'databases_json/{db_name}.json'

def change_leader(team_id):
    conn = db_connect(db_path('teams.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT ")