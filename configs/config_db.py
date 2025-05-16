import os

def db_path(db_name):
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database', db_name)
    db_path = os.path.abspath(db_path)
    return db_path
