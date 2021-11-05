
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

RESET_CODE_COLORS = ['red', 'green', 'blue', 'cyan', 'magenta', 'yellow', 'orange', 'white']
RESET_CODE_CHAR_BITS = 3
RESET_CODE_LEN = 6
RESET_CODE_TIMEOUT = 60


_reset_code: Optional[str] = None
_reset_code_time: float = 0


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


def generate_reset_code() -> List[str]:
    global _reset_code, _reset_code_time

    code_list = [secrets.randbits(RESET_CODE_CHAR_BITS) for _ in range(RESET_CODE_LEN)]
    _reset_code = ''.join([RESET_CODE_COLORS[c][0] for c in code_list])
    _reset_code_time = time.time()
    colors = [RESET_CODE_COLORS[c] for c in code_list]

    logging.debug(f'reset code is "{_reset_code}"')

    return colors


def verify_reset_code(code: str) -> bool:
    global _reset_code

    # Check if password expired
    if time.time() - _reset_code_time > RESET_CODE_TIMEOUT:
        return False

    # Check if unset
    if _reset_code is None:
        return False

    if _reset_code == code or _reset_code == code[::-1]:
        _reset_code = None
        return True

    return False
