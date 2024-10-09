import logging

from utils import get_logger


class HttpTimeout(Exception):
    def __init__(self, proxy=None, url=None, logger: logging.Logger = None):
        # Call the base class constructor with the parameters it needs
        message = f"Timeout HTTP:\n" f"\tUrl: {url}\n" f"\tProxy: {proxy}"
        super().__init__(message)
        self.proxy = proxy
        self.url = url
        if not logger:
            logger = get_logger("common.log", logging.DEBUG)
        logger.error(message)


class BadStatus(Exception):
    def __init__(
        self, proxy=None, url=None, status=None, logger: logging.Logger = None
    ):
        # Call the base class constructor with the parameters it needs
        message = (
            "Bad HTTP status:\n"
            f"\tUrl: {url}\n"
            f"\tProxy: {proxy}"
            f"\tStatus: {status}"
        )
        super().__init__(message)
        self.proxy = proxy
        self.url = url
        self.status = status
        if not logger:
            logger = get_logger("common.log", logging.DEBUG)
        logger.error(message)
