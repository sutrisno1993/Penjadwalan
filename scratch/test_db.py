import logging
logging.basicConfig(level=logging.INFO)
print("Importing init_db...")
from backend.database import init_db
print("Calling init_db()...")
init_db()
print("init_db() complete!")
