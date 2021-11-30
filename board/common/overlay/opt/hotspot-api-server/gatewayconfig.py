
import logging

import asyncsubprocess


ENABLE_PAIR_CMD = 'HOME=/tmp /opt/gateway_config/bin/gateway_config advertise on'


async def enable_pair() -> None:
    logging.info('enabling pairing')

    try:
        output = await asyncsubprocess.check_output(ENABLE_PAIR_CMD)
    except asyncsubprocess.StatusCodeError as e:
        # gateway_config advertise command always returns exit code 1
        output = (e.stderr or e.stdout).strip()

    if output != 'ok':
        logging.error(f'gateway_config advertise command: {output}')
        raise Exception(f'Unexpected gateway-config output: {output}')
