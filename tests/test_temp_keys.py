import datetime

import pytest

from raspberrylock.temp_keys import add_temp_key


FAKE_DB_CONTENT = """{"_default": {
    "1": {
        "username": "nobody", 
        "start_datetime": "{TinyDate}:2024-05-03T01:06:18.975330", 
        "duration": 30
    }
}}
"""


@pytest.fixture
def fake_database_path(tmp_path):
    p = tmp_path / "hello.json"
    p.write_text(FAKE_DB_CONTENT)
    return p


def test_add_temp_key(fake_database_path):
    start = datetime.datetime.now()
    # Second entry gets the correct ID (2)
    assert 2 == add_temp_key(fake_database_path, 'bernd', start, 30)
