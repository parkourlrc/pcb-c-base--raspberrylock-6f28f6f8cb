import pytest

from raspberrylock.gpio_tasks import decode_keypad

def test_decode_keypad():
    key_1 = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 1]]
    assert decode_keypad(key_1) == '1'