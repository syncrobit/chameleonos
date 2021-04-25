
import logging
import subprocess


ENABLE_PAIR_CMD = 'HOME=/tmp /opt/gateway_config/bin/gateway_config advertise on'


def enable_pair() -> None:
    logging.info('enabling pairing')

    try:
        output = subprocess.check_output(ENABLE_PAIR_CMD, shell=True).decodee().strip()

    except subprocess.CalledProcessError as e:
        # gateway_config advertise command always returns exit code 1
        output = (e.stderr or e.stdout or b'').decode().strip()

    if output != 'ok':
        logging.error(f'gateway_config advertise command: {output}')
        raise Exception(f'Unexpected gateway-config output: {output}')
