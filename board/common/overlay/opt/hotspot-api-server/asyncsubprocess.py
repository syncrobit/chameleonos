
import asyncio


DEF_TIMEOUT = 60  # seconds


class StatusCodeError(Exception):
    def __init__(self, msg: str, stdout: str, stderr: str) -> None:
        self.stdout: str = stdout
        self.stderr: str = stderr

        super().__init__(msg)


async def check_output(cmd: str, timeout=DEF_TIMEOUT, strip: bool = True) -> str:
    p = await asyncio.wait_for(
        asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE),
        timeout=timeout
    )
    stdout_data, stderr_data = await p.communicate()
    stdout_data = (stdout_data or b'').decode()
    stderr_data = (stderr_data or b'').decode()
    if p.returncode != 0:
        raise StatusCodeError('Command returned non-zero exit status', stdout_data, stderr_data)

    stdout_data = stdout_data
    if strip:
        stdout_data = stdout_data.strip()

    return stdout_data


async def check_call(cmd: str, timeout=DEF_TIMEOUT) -> None:
    p = await asyncio.wait_for(
        asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL),
        timeout=timeout
    )
    await p.communicate()
    stdout_data, stderr_data = await p.communicate()
    stdout_data = (stdout_data or b'').decode()
    stderr_data = (stderr_data or b'').decode()
    if p.returncode != 0:
        raise StatusCodeError('Command returned non-zero exit status', stdout_data, stderr_data)
