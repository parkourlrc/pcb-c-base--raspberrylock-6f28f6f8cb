from pathlib import Path
from datetime import datetime

from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer


# Setup serialization to be able to automatically serialize datetime
# instances to JSON:
serialization = SerializationMiddleware(JSONStorage)
serialization.register_serializer(DateTimeSerializer(), 'TinyDate')


def add_temp_key(database_filename: Path, username: str, start_datetime: datetime, duration: int):
    """
    Add a temporary key for one user.
    """
    db = TinyDB(database_filename, storage=serialization)
    #User = Query()
    #db.insert({'name': 'John', 'age': 22})
    entry_id = db.insert({
        "username": username,
        "start_datetime": start_datetime,
        "duration": duration,
    })
    return entry_id