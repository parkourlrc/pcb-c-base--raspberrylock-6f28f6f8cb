import base64
import hashlib
import logging
from datetime import datetime

log = logging.getLogger(__name__)


# import config
from ldap3 import Server, Connection, ALL


class LDAP:
    URI = 'ldaps://lea.cbrp3.c-base.org'
    # URI = 'ldaps://dea.cbrp3.c-base.org'
    BASE = 'dc=c-base,dc=org'
    USERBASE = 'ou=crew'
    BINDDN = 'cn=c-labpin,ou=bind,dc=c-base,dc=org'
    BINDPW = '**********************'
    PINFIELD = 'c-labPIN'
    UIDFIELD = 'uid'

    ##ALLOWED: CREW (ALL)
    ACCESS_FILTER = '(&(uidNumber={})(memberof=cn=crew,ou=groups,dc=c-base,dc=org)(memberof=cn=crew,ou=groups,dc=c-base,dc=org))'

    ##ALLOWED: CEY-C-LAB
    # ACCESS_FILTER = '(&(uidNumber={})(memberof=cn=cey-c-lab,ou=groups,dc=c-base,dc=org)(memberof=cn=crew,ou=groups,dc=c-base,dc=org))'

    ##ALLOWED: CEY-SCHLEUSE
    # ACCESS_FILTER = '(&(uidNumber={})(memberof=cn=cey-schleuse,ou=groups,dc=c-base,dc=org)(memberof=cn=crew,ou=groups,dc=c-base,dc=org))'

    ##ALLOWED: CEY-SCHLEUSE, CEY-C-LAB
    # ACCESS_FILTER = '(&(uidNumber={})(|(memberof=cn=cey-c-lab,ou=groups,dc=c-base,dc=org)(memberof=cn=cey-schleuse,ou=groups,dc=c-base,dc=org))(memberof=cn=crew,ou=groups,dc=c-base,dc=org))'

    ##ALLOWED: CEY-SCHLEUSE, CEY-C-LAB, CEY-SOUNDLAB
    # ACCESS_FILTER = '(&(uidNumber={})(|(memberof=cn=cey-c-lab,ou=groups,dc=c-base,dc=org)(memberof=cn=cey-soundlab,ou=groups,dc=c-base,dc=org)(memberof=cn=cey-schleuse,ou=groups,dc=c-base,dc=org))(memberof=cn=crew,ou=groups,dc=c-base,dc=org))'


def ldap_connect():
    server = Server('lea.cbrp3.c-base.org', use_ssl=True)
    conn = Connection(server, user=LDAP.BINDDN, password=LDAP.BINDPW)
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


def authenticate(uid, pin):
    conn, server = ldap_connect()
    try:
        is_found = conn.search(
            ','.join([LDAP.USERBASE, LDAP.BASE]),
            LDAP.ACCESS_FILTER.format(uid),
            attributes=[LDAP.UIDFIELD, LDAP.PINFIELD, 'uid']
        )
        if not is_found:
            log.error("conn.search did not find anything")
            return False
        user = conn.entries[0]
        username = str(user[LDAP.UIDFIELD])
        hashed = str(user[LDAP.PINFIELD])
        if pwcheck(hashed, pin):
            log.warning('Valid combination for user "%s". Opening lock' % username)
            conn.unbind()
            return True
    except Exception as e:
        log.error('Invalid user/pin: %s (%s)' % (uid, str(e)))
    if not conn.closed:
        conn.unbind()
    return False


numbuf = []


