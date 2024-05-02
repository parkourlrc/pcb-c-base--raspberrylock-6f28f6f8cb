from pathlib import Path
from datetime import datetime

from tinydb import TinyDB, Query


def add_temp_key(database_filename: Path, username: str, start_datetime: datetime, duration: int):
    """
    Add a temporary key for one user.
    """
    db = TinyDB()
    User = Query()
    db.insert({'name': 'John', 'age': 22})