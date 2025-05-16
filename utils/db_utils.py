import sqlite3
from sqlite3 import Error



def db_connect(db_path:str):
    connect = None 
    try:
        connect = sqlite3.connect(db_path)
        return connect
    except Error as e:
        print(f'\nERROR: in utils/db_utils.db_connect (db: {db_path}): {e}\n')
    return connect