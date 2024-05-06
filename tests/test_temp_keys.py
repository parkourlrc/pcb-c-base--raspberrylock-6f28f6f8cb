import datetime
from pathlib import Path
import pytest

# unit under test
from raspberrylock.temp_keys import add_temp_key, look_for_temp_key, cleanup_database, get_all_temp_keys


FAKE_DB_CONTENT = """
{
    "_default": {
        "1": {
            "username": "nobody", 
            "start_datetime": "{TinyDate}:2024-05-03T01:06:18.975330+00:00", 
            "duration": 30
        }
    }
}
"""


@pytest.fixture
def fake_database_path(tmp_path) -> Path:
    p = tmp_path / "hello.json"
    p.write_text(FAKE_DB_CONTENT)
    return p


def test_add_temp_key(fake_database_path):
    start = datetime.datetime.now(tz=datetime.UTC)
    # Second entry gets the correct ID (2)
    assert 2 == add_temp_key(fake_database_path, 'bernd', start, 30)
    later = datetime.datetime.now(tz=datetime.UTC)
    assert True == look_for_temp_key(fake_database_path, 'bernd', later)


def test_look_for_temp_key(fake_database_path):
    valid_datetime = datetime.datetime(2024, 5, 3, 19, 0, 0, tzinfo=datetime.UTC)
    assert True == look_for_temp_key(fake_database_path, 'nobody', valid_datetime)

    # check if the temp key is invalid after expiration date.
    after_expiration = datetime.datetime(2024, 7, 3, 19, 0, 0, tzinfo=datetime.UTC)
    assert False == look_for_temp_key(fake_database_path, 'nobody', after_expiration)


def test_clean_database(fake_database_path):
    one_month_later = datetime.datetime(2024, 6, 4, 0, 0, 0, tzinfo=datetime.UTC)
    assert None == cleanup_database(fake_database_path, one_month_later)

    assert 0 == len(get_all_temp_keys(fake_database_path))


def test_get_all_temp_keys(fake_database_path):
    assert 1 == len(get_all_temp_keys(fake_database_path))