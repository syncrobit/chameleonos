
import logging
import os


SEND_LOGS_ACTIVE_FILE = '/var/run/send_logs_active'


def enable_logs_sending() -> None:
    logging.info('enabling logs sending')
    with open(SEND_LOGS_ACTIVE_FILE, 'w'):
        pass


def disable_logs_sending() -> None:
    logging.info('disabling logs sending')
    try:
        os.remove(SEND_LOGS_ACTIVE_FILE)

    except IOError:
        pass
