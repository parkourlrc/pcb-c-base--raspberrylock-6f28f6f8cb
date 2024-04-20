from raspberrylock.ldap_interface import pwcheck


def test_pwcheck():
    assert pwcheck('{SSHA}c8pLDYbSkF2jBAKxxa67nY7NYkdQXiPNFzzRso9FRZI=', '1234') == True