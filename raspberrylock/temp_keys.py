import datetime
from pathlib import Path

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
    """
    Returns `True` if there exists a valid temp key for the user.
    """
    if valid_at is None:
        valid_at = datetime.datetime.now(tz=datetime.UTC)
    
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


def cleanup_database(database_filename: Path, valid_at: datetime=None) -> None:
    """
    Remove any expired tempkeys
    """
    if valid_at is None:
        valid_at = datetime.datetime.now(tz=datetime.UTC)

    db = TinyDB(database_filename, storage=serialization)
    TempKey = Query()
    for temp_key in db.all():
        start_date = temp_key['start_datetime']
        end_date = start_date + datetime.timedelta(days=temp_key['duration'])

        if valid_at > end_date:
            # delete the expired temp key
            db.remove(doc_ids=[temp_key.doc_id])


def get_all_temp_keys(database_filename: Path) -> list:
    """
    List all temporary keys
    """
    db = TinyDB(database_filename, storage=serialization)
    return list(db.all())
