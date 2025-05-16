from utils import add_feedback
from utils import del_feedback
from utils.db_utils import db_connect
from configs import db_path

# conn = db_connect(db_path('users.db'))
# cursor = conn.cursor()

# cursor.execute("""
#         CREATE TABLE IF NOT EXISTS users (
#             user_id INTEGER PRIMARY KEY,
#             username INTEGER NOT NULL,
#             team_id INTEGER,
#             is_leader BOOLEAN,
#             is_admin BOOLEAN,
#             feedbacks_count INTEGER,
#             reg_date TEXT,
#             user_name TEXT,
#             user_lastname TEXT
#         )
#         """)

# print('Успех')
# conn.commit()

"""
добавление столбца
"""
# conn = db_connect(db_path('teams.db'))
# cursor = conn.cursor()
# cursor.execute("ALTER TABLE teams ADD COLUMN invite_hash")
# conn.commit()

# add_feedback(234, 234, 'dfg', '435', 'dfg')
# del_feedback(1)

