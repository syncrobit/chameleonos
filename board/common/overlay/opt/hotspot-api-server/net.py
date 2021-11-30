
from typing import Optional

import asyncsubprocess


DOWNLOAD_SPEED_TEST_URL = 'http://speedtest-blr1.digitalocean.com/10mb.test'
DOWNLOAD_SPEED_TEST_TIMEOUT = 10  # seconds
DOWNLOAD_SPEED_TEST_CMD = (
    f'speed=$( '
    f'    curl -o /dev/null -m {DOWNLOAD_SPEED_TEST_TIMEOUT} {DOWNLOAD_SPEED_TEST_URL} 2>&1 | '
    f'    grep -v "timed out" | tail -n 1 | tr -s " " | rev | cut -d " " -f 1 | rev | sed -r "s/([0-9]+)/\\1 /" '
    f'); '
    f'[[ "$speed" =~ ^[0-9] ]] || speed=0; speed=($speed); '
    f'if [[ ${{#speed[@]}} -gt 1 ]]; then '
    f'    speed=${{speed[0]}}; '
    f'    unit=${{speed[1]}}; '
    f'    [[ ${{unit}} == M ]] && speed=$(echo "${{speed}} * 1024" | bc -l); '
    f'else '
    f'    speed=$(echo "${{speed}} / 1024" | bc -l); '
    f'fi; '
    f'printf "%.1f" ${{speed}}'
)

LATENCY_TEST_CMD = 'ping -A -c 5 8.8.8.8 | tail -n 1 | cut -d "/" -f 4 | cut -d "." -f 1'

PUBLIC_IP_CMD = 'curl -4 -s https://ipv4.icanhazip.com/'


async def test_download_speed() -> int:
    """Return download speed in kB/s."""
    try:
        return int(float(await asyncsubprocess.check_output(DOWNLOAD_SPEED_TEST_CMD)))
    except Exception:
        return 0


async def test_latency() -> int:
    """Return network latency in milliseconds."""

    try:
        return int(await asyncsubprocess.check_output(LATENCY_TEST_CMD))
    except Exception:
        return 0


async def get_public_ip() -> Optional[str]:
    try:
        return await asyncsubprocess.check_output(PUBLIC_IP_CMD)
    except Exception:
        pass
