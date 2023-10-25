#!/usr/bin/env python3
from os import walk, path as ospath
from aiofiles.os import remove as aioremove, path as aiopath, listdir, rmdir, makedirs
from aioshutil import rmtree as aiormtree
from shutil import rmtree, disk_usage
from magic import Magic
from re import split as re_split, I, search as re_search
from subprocess import run as srun
from sys import exit as sexit

from .exceptions import NotSupportedExtractionArchive
from worker import LOGGER, DOWNLOAD_DIR
from worker.helper.ext_utils.bot_utils import sync_to_async, cmd_exec


FIRST_SPLIT_REGEX = r'(\.|_)part0*1\.rar$|(\.|_)7z\.0*1$|(\.|_)zip\.0*1$|^(?!.*(\.|_)part\d+\.rar$).*\.rar$'

SPLIT_REGEX = r'\.r\d+$|\.7z\.\d+$|\.z\d+$|\.zip\.\d+$'


async def start_cleanup():
    try:
        await aiormtree(DOWNLOAD_DIR)
    except:
        pass
    await makedirs(DOWNLOAD_DIR)


def exit_clean_up(signal, frame):
    try:
        LOGGER.info(
            "Please wait, while we clean up and stop the running downloads")
        srun(['pkill', '-9', '-f', 'gunicorn'])
        sexit(0)
    except KeyboardInterrupt:
        LOGGER.warning("Force Exiting before the cleanup finishes!")
        sexit(1)

def check_storage_threshold(size, threshold, arch=False, alloc=False):
    free = disk_usage(DOWNLOAD_DIR).free
    if not alloc:
        if (not arch and free - size < threshold or arch and free - (size * 2) < threshold):
            return False
    elif not arch:
        if free < threshold:
            return False
    elif free - size < threshold:
        return False
    return True
