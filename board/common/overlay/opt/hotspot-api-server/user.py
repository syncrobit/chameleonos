
import hashlib
import logging
import os
import pubkey
import secrets
import time

from typing import List, Optional


CREDENTIALS_FILE = '/var/lib/api_credentials'
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'admin'
INTERNAL_USERNAME = 'dashboard'

TEMPORARY_PASSWORD_COLORS = ['red', 'green', 'blue', 'cyan', 'magenta', 'yellow', 'orange', 'white']
TEMPORARY_PASSWORD_CHAR_BITS = 3
TEMPORARY_PASSWORD_LEN = 6
TEMPORARY_PASSWORD_TIMEOUT = 60


_temporary_password: Optional[str] = None
_temporary_password_time: float = 0


def verify_credentials_internal(username: str, password: str) -> bool:
    if username != INTERNAL_USERNAME:
        return False

    actual_password = f'{pubkey.get_pub_key_hex()}:{pubkey.get_ecc_sn()}'
    actual_password = hashlib.sha256(actual_password.encode()).hexdigest()

    if password != actual_password:
        logging.error('internal password mismatch')
        return False

    return True


def verify_credentials(username: str, password: str) -> bool:
    if verify_credentials_internal(username, password):
        return True

    if os.path.exists(CREDENTIALS_FILE) and os.path.getsize(CREDENTIALS_FILE) > 0:
        with open(CREDENTIALS_FILE, 'rt') as f:
            actual_username, actual_password = f.readline().strip().split(':', 1)

    else:
        actual_username = DEFAULT_USERNAME
        actual_password = DEFAULT_PASSWORD

    if username != actual_username:
        logging.error('unknown username %s', username)
        return False

    if password != actual_password:
        logging.error('password mismatch')
        return False

    return True


def set_password(username: str, password: str) -> None:
    logging.info('setting password for %s', username)

    with open(CREDENTIALS_FILE, 'wt') as f:
        f.write(f'{username}:{password}')


def generate_temporary_password() -> List[str]:
    global _temporary_password, _temporary_password_time

    password_list = [secrets.randbits(TEMPORARY_PASSWORD_CHAR_BITS) for _ in range(TEMPORARY_PASSWORD_LEN)]
    _temporary_password = ''.join([TEMPORARY_PASSWORD_COLORS[c][0] for c in password_list])
    _temporary_password_time = time.time()
    colors = [TEMPORARY_PASSWORD_COLORS[c] for c in password_list]

    logging.debug(f'temporary password is "{_temporary_password}"')

    return colors


def verify_temporary_password(password: str) -> bool:
    global _temporary_password

    # Check if password expired
    if time.time() - _temporary_password_time > TEMPORARY_PASSWORD_TIMEOUT:
        return False

    # Check if unset
    if _temporary_password is None:
        return False

    if _temporary_password == password or _temporary_password == reversed(password):
        _temporary_password = None
        return True

    return False
