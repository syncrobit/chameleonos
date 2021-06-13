
import logging
import os


CREDENTIALS_FILE = '/var/lib/api_credentials'
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'admin'


def verify_credentials(username: str, password: str) -> bool:
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
