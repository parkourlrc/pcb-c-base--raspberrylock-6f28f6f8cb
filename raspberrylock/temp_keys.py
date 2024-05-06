from pathlib import Path
import datetime

from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer


# Setup serialization to be able to automatically serialize datetime
# instances to JSON:
serialization = SerializationMiddleware(JSONStorage)
serialization.register_serializer(DateTimeSerializer(), 'TinyDate')


def add_temp_key(database_filename: Path, username: str, 
                 start_datetime: datetime.datetime, duration: int) -> int:
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


def look_for_temp_key(database_filename: Path, username: str, valid_at: datetime=None) -> bool:
    if valid_at is None:
        valid_at = datetime.datetime.now(tz=datetime.utc)
    
    db = TinyDB(database_filename, storage=serialization)
    TempKey = Query()
    
    for temp_key in db.search(TempKey.username == username):
        start_date = temp_key['start_datetime']
        end_date = start_date + datetime.timedelta(days=temp_key['duration'])
        if valid_at <= end_date and valid_at >= start_date:
            # temporary key is valid
            return True
    
    # No key was found
    return False
