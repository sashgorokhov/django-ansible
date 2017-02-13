import subprocess
import logging

logger = logging.getLogger(__name__)


def _try_decode(b):
    try:
        return b.decode()
    except:
        return b


def run(executable, args, env=None, cwd=None, **kwargs):
    """
    :param kwargs: Additional arguments passed to subprocess.run function
    :rtype: subprocess.CompletedProcess
    """
    completed = subprocess.run(
        args=args,
        executable=executable,
        env=env,
        cwd=cwd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **kwargs
    )
    logger.info('$ %s %s (env: %s)', executable, str(args), str(env))
    if completed.returncode != 0:
        logger.warning('Exited with code %s', completed.returncode)
    if completed.stderr:
        logger.warning(_try_decode(completed.stderr))
    if completed.stdout:
        logger.debug(_try_decode(completed.stdout))
    return completed

