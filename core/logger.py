import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")

_logger = None


def setup_logger():
    global _logger
    if _logger is not None:
        return _logger

    os.makedirs(LOG_DIR, exist_ok=True)

    _logger = logging.getLogger("firewall_platform")
    _logger.setLevel(logging.DEBUG)

    if _logger.handlers:
        return _logger

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s %(name)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(file_formatter)

    _logger.addHandler(file_handler)
    _logger.addHandler(console_handler)

    return _logger


def get_logger():
    if _logger is None:
        return setup_logger()
    return _logger


logger = get_logger()
