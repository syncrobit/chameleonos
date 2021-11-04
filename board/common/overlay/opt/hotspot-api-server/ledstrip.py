
import asyncio

from typing import Any, Dict, List, Optional

import logging
import os
import subprocess


RESTART_CMD = 'service ledstate restart'
CONF_FILE = '/data/etc/ledstrip.conf'
SYS_CONF_FILE = '/etc/ledstrip.conf'
STATE_FILE = '/var/run/led_state'
PAUSE_FILE = '/var/run/led_pause'
DEF_STATE = 'powered_up'
LED_STRIP_PROG = '/usr/bin/ledstrip'


_resume_later_task: Optional[asyncio.Task] = None


def get_current_state() -> str:
    try:
        with open(STATE_FILE, 'rt') as f:
            return f.read().strip()
    except Exception:
        return DEF_STATE


def get_config(conf_file: Optional[str] = None) -> Dict[str, Any]:
    if conf_file is None:
        config = get_config(SYS_CONF_FILE)
        conf_file = CONF_FILE

    else:
        config = {
            'brightness': 50,
            'ok_color': 'green'
        }

    if not os.path.exists(conf_file):
        return config

    with open(conf_file, 'rt') as f:
        for line in f:
            line = line.strip()
            try:
                k, v = line.split('=', 1)

            except ValueError:
                continue

            k = k[10:].lower()  # Skip LED_STRIP_
            try:
                v = int(v)

            except ValueError:
                try:
                    v = float(v)

                except ValueError:
                    pass

            config[k] = v

    return config


def set_config(config: Dict[str, Any]) -> None:
    logging.info('updating ledstrip config: %s', config)

    # Use default values for null entries
    default_config = get_config(SYS_CONF_FILE)
    for k, v in config.items():
        if v is None:
            config[k] = default_config[k]

    # Use current values for missing entries
    current_config = get_config()
    for k, v in current_config.items():
        config.setdefault(k, v)

    with open(CONF_FILE, 'wt') as f:
        for k, v in config.items():
            if v is None:
                continue

            k = f'LED_STRIP_{k.upper()}'
            line = f'{k}={v}\n'
            f.write(line)


def _set(params: List[str]) -> None:
    cmd = [LED_STRIP_PROG] + params
    subprocess.check_call(cmd)


def _get_def_brightness() -> int:
    cmd = (
        f'test -f {SYS_CONF_FILE} && source {SYS_CONF_FILE};'
        f'test -f {CONF_FILE} && source {CONF_FILE};'
        'echo $LED_STRIP_BRIGHTNESS'
    )
    return int(subprocess.check_output(cmd, shell=True).decode().strip())


def set_on(color: str, brightness: int = -1) -> None:
    if brightness < 0:
        brightness = _get_def_brightness()
    _set(['on', f'{brightness}', f'{color}'])


def set_off() -> None:
    _set(['off'])


def fade_in(color: str, colors: Optional[List[str]] = None, brightness: int = -1) -> None:
    if brightness < 0:
        brightness = _get_def_brightness()
    colors = colors or []
    _set(['fadein', f'{brightness}', f'{color}'] + colors)


def fade_out(color: str, colors: Optional[List[str]] = None, brightness: int = -1) -> None:
    if brightness < 0:
        brightness = _get_def_brightness()
    colors = colors or []
    _set(['fadeout', f'{brightness}', f'{color}'] + colors)


def progress_lr(color: str, colors: Optional[List[str]] = None, brightness: int = -1) -> None:
    if brightness < 0:
        brightness = _get_def_brightness()
    colors = colors or []
    _set(['progresslr', f'{brightness}', f'{color}'] + colors)


def progress_rl(color: str, colors: Optional[List[str]] = None, brightness: int = -1) -> None:
    if brightness < 0:
        brightness = _get_def_brightness()
    colors = colors or []
    _set(['progressrl', f'{brightness}', f'{color}'] + colors)


def set_pattern(colors: List[str], brightness: int = -1) -> None:
    if brightness < 0:
        brightness = _get_def_brightness()
    _set(['pattern', f'{brightness}'] + colors)


async def pause(duration: Optional[int] = None) -> None:
    global _resume_later_task

    if _resume_later_task:
        _resume_later_task.cancel()
        _resume_later_task = None

    if duration:
        logging.info('pausing ledstrip for %s seconds', duration)
    else:
        logging.info('pausing ledstrip')

    if duration:

        async def resume_later():
            await asyncio.sleep(duration)
            await resume()

        _resume_later_task = asyncio.create_task(resume_later())

    with open(PAUSE_FILE, 'w'):
        pass

    # Wait until ledstrip program exits
    while True:
        try:
            subprocess.check_output(f'ps aux | grep {LED_STRIP_PROG} | grep -vq grep', shell=True)
            await asyncio.sleep(0.1)
        except Exception:
            break


async def resume() -> None:
    global _resume_later_task

    if _resume_later_task:
        _resume_later_task.cancel()
        _resume_later_task = None

    logging.info('resuming ledstrip')
    try:
        os.remove(PAUSE_FILE)
    except IOError:
        pass


def restart() -> None:
    logging.info('restarting ledstrip')
    subprocess.check_call(RESTART_CMD, shell=True)
