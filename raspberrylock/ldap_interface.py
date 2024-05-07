import base64
import hashlib
import logging
from datetime import datetime

log = logging.getLogger(__name__)


# import config
from ldap3 import Server, Connection, ALL


def ldap_connect(LDAP):
    server = Server('lea.cbrp3.c-base.org', use_ssl=True)
    conn = Connection(server, user=LDAP['BINDDN'], password=LDAP['BINDPW'])
    conn.open()
    if not conn.bind():
        log.error('error in bind: %s' % conn.result)
    return conn, server


def pwcheck(record, pw):
    """
    Checks if the entered PIN was correct.
    """
    if not record.startswith('{SSHA}'):
        return record == pw
    bd = base64.b64decode(bytearray(record[6:], 'UTF-8'))
    hashv = bd[:20]
    salt = bd[20:]
    newhashv = hashlib.sha1(bytearray(pw, 'UTF-8')+salt).digest()
    return hashv == newhashv


def authenticate(LDAP, uid, pin, is_fallback=False):
    if is_fallback is True:
        filter = LDAP['ACCESS_FILTER_FALLBACK'].format(uid)
    else:
        filter = LDAP['ACCESS_FILTER'].format(uid)
    log.info("Using filter %s" % repr(filter))
    conn, server = ldap_connect(LDAP)
    try:
        is_found = conn.search(
            ','.join([LDAP['USERBASE'], LDAP['BASE']]),
            filter,
            attributes=[LDAP['UIDFIELD'], LDAP['PINFIELD'], 'uid']
        )
        if not is_found:
            log.error("conn.search did not find anything")
            return False
        user = conn.entries[0]
        username = str(user[LDAP['UIDFIELD']])
        hashed = str(user[LDAP['PINFIELD']])
        if pwcheck(hashed, pin):
            log.warning('Valid combination for user "%s". Opening lock' % username)
            conn.unbind()
            return True
    except Exception as e:
        log.error('Invalid user/pin: %s (%s)' % (uid, str(e)))
    if not conn.closed:
        conn.unbind()
    return False


def find_user_fallback(LDAP, uid):
    """
    Return the username of valid fallback user (used to find the temporary key)

    Returns `False` if the user cannot be found.
    """
    conn, server = ldap_connect(LDAP)
    try:
        is_found = conn.search(
            ','.join([LDAP['USERBASE'], LDAP['BASE']]),
            LDAP['ACCESS_FILTER_FALLBACK'].format(uid),
            attributes=[LDAP['UIDFIELD'], LDAP['PINFIELD'], 'uid']
        )
        if not is_found:
            log.error("conn.search did not find anything")
            return False
        else:
            user = conn.entries[0]
            username = str(user[LDAP['UIDFIELD']])
            return username
    
    except Exception as e:
        log.error('Invalid user/pin: %s (%s)' % (uid, str(e)))
    if not conn.closed:
        conn.unbind()
    return False



numbuf = []
