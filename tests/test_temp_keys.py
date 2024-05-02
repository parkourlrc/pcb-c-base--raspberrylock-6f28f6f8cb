import pytest


CONTENT = """[{
    "username": "bernd",
    "start_datetime": "2024-04-30T18:29:28.015212+00:00",
    "duration": 30
}]
"""


@pytest.fixture
def fake_database(tmp_path):
    p = tmp_path / "hello.json"
    p.write_text(CONTENT)

def test_add_temp_key():
    