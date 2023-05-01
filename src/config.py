import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_URL = "data/db.sqlite3"
START_POSITION_CODE = sum(2 ** (7 * i) for i in range(7))
