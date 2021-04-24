
from typing import Any, Dict, Optional

import logging
import re
import subprocess


PF_RESTART_CMD = 'service packetforwarder restart'
PF_CONCENTRATOR_MODEL_CMD = 'ps aux | grep /opt/packet_forwarder/bin/lora_pkt_fwd_ | grep -v grep'
SYS_CONF_FILE = '/opt/packet_forwarder/etc/global_conf.json.{model}.{region}'
CONF_FILE = '/var/lib/global_conf.json'


def get_concentrator_model() -> Optional[str]:
    try:
        output = subprocess.check_output(PF_CONCENTRATOR_MODEL_CMD, shell=True)
        prog_path = output.split()[-1].decode()
        return re.search(r'sx\d+', prog_path).group()

    except Exception:
        pass


# def get_region() -> Optional[str]:
#     try:
#         with open(REG_FILE, 'rt') as f:
#             return re.search(r'REGION=([a-zA-Z0-9])', f.read()).group(1)
#     except Exception:
#         pass
#
#
# def get_nat_config() -> Dict[str, Any]:
#     nat = {
#         'external_ip': None,
#         'external_port': None,
#         'internal_port': None
#     }
#
#     with open(NAT_FILE, 'rt') as f:
#         for line in f:
#             line = line.strip()
#             try:
#                 k, v = line.split('=', 1)
#
#             except ValueError:
#                 continue
#
#             k = k[4:].lower()  # Skip NAT_
#             if k.endswith('port'):
#                 try:
#                     v = int(v)
#
#                 except ValueError:
#                     continue
#
#             nat[k] = v
#
#     return nat
#
#
# def set_nat_config(nat: Dict[str, Any]) -> None:
#     logging.info('updating NAT config: %s', nat)
#
#     # Use current values for missing entries
#     current_nat = get_nat_config()
#     for k, v in current_nat.items():
#         nat.setdefault(k, v)
#
#     with open(NAT_FILE, 'wt') as f:
#         for k, v in nat.items():
#             if v is None:
#                 continue
#
#             k = f'NAT_{k.upper()}'
#             line = f'{k}={v}\n'
#             f.write(line)


def restart() -> None:
    subprocess.check_output(PF_RESTART_CMD, shell=True)
