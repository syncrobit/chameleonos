
import subprocess


ENABLE_PAIR_CMD = 'HOME=/tmp /opt/gateway_config/bin/gateway_config advertise on'


def enable_pair() -> None:
    try:
        subprocess.check_output(ENABLE_PAIR_CMD, shell=True)

    except Exception:
        pass
