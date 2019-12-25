# -*- coding: utf-8 -*
"""logger.py

:DATE: 2019/12/25 18:32:24

LOGGING SETTING FOR OpenPraat

"""
from pathlib import Path
import logging
import sys

LOGGINGDIR = Path.home().joinpath(".local", "share", "open-praat", "logs")


def createLogger(name):
    """Logger の初期化を行います"""
    formatter = logging.Formatter(
        '%(asctime)s:%(name)s:%(levelname)s:%(message)s'
    )
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)

    Path(LOGGINGDIR).mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(
        str(LOGGINGDIR.joinpath("{}.log".format(name)))
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    logger.addHandler(file_handler)
    return logger
