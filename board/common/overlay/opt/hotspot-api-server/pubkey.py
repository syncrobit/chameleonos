
from typing import Optional

import re


PUB_KEY_HEX_FILE = '/var/run/public_key_hex'
PUB_KEYS_FILE = '/var/run/public_keys'
ECC_SN_FILE = '/var/run/ecc_sn'


def get_pub_key_hex() -> Optional[str]:
    try:
        with open(PUB_KEY_HEX_FILE, 'rt') as f:
            return f.read().strip()

    except Exception:
        pass


def get_address() -> Optional[str]:
    try:
        with open(PUB_KEYS_FILE, 'rt') as f:
            return re.search(r'[a-zA-Z0-9]{50,}', f.read()).group()

    except Exception:
        pass


def get_name() -> Optional[str]:
    try:
        with open(PUB_KEYS_FILE, 'rt') as f:
            return re.search(r'\w+-\w+-\w+', f.read()).group()

    except Exception:
        pass


def get_ecc_sn() -> Optional[str]:
    try:
        with open(ECC_SN_FILE, 'rt') as f:
            return f.read().strip()

    except Exception:
        pass
