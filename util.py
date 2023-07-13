import logging

from env import LOG_LEVEL


def get_logger(name: str) -> logging.Logger:
    """Returns a logger with the given name"""
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    # create console handler with a higher log level
