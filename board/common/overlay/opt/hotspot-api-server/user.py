
import hashlib
import logging
import os
import pubkey


CREDENTIALS_FILE = '/var/lib/api_credentials'
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'admin'
INTERNAL_USERNAME = 'dashboard'


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
