import logging

from utils import get_logger


# this exception - delete session file and change proxy, if repeat - ACCAUNTU PIZDEC
class TelegramBadConvertProfile(BaseException):
    def __init__(
        self, profile_path, papa_Exception: Exception, logger: logging.Logger = None
    ):
        message = (
            f"Failed to convert TDATA to Telethon session:\n"
            f"\tPath: {profile_path}\n"
            f"\tPapa Exception -  type: {type(papa_Exception)}, message: {papa_Exception}"
        )
        super().__init__(message)
        self.profile_Path = profile_path
        if not logger:
            logger = get_logger("common.log", logging.DEBUG)
        logger.error(message)


# this exception - tdata broken 100%
class TelegramBadProfile(BaseException):
    def __init__(
        self, profile_path, papa_Exception: Exception, logger: logging.Logger = None
    ):
        message = (
            f"Failed to load TDATA:\n"
            f"\tPath: {profile_path}\n"
            f"\tPapa Exception -  type: {type(papa_Exception)}, message: {papa_Exception}"
        )
        super().__init__(message)
        self.profile_Path = profile_path
        if not logger:
            logger = get_logger("common.log", logging.DEBUG)
        logger.error(message)


class HttpTimeout(BaseException):
    def __init__(self, proxy, url, logger: logging.Logger = None):
        # Call the base class constructor with the parameters it needs
        message = f"Timeout HTTP:\n" f"\tUrl: {url}\n" f"\tProxy: {proxy}"
        super().__init__(message)
        self.proxy = proxy
        self.url = url
        if not logger:
            logger = get_logger("common.log", logging.DEBUG)
        logger.error(message)


class HttpError(BaseException):
    def __init__(
        self, proxy, url, papa_Exception: BaseException, logger: logging.Logger = None
    ):
        # Call the base class constructor with the parameters it needs
        message = (
            f"Failed HTTP request:\n"
            f"\tUrl: {url}\n"
            f"\tProxy: {proxy}"
            f"\tPapa Exception -  type: {type(papa_Exception)}, message: {papa_Exception}"
        )
        super().__init__(message)
        self.proxy = proxy
        self.url = url
        if not logger:
            logger = get_logger("common.log", logging.DEBUG)
        logger.error(message)


class BadStatus(BaseException):
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
