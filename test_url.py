import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
print(repr(db_url))
print(repr(db_url.replace("%", "%%")))
