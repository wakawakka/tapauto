import logging
from uuid import uuid4


def get_logger(filepath=None, level=logging.INFO) -> logging.Logger:
    logger_id = uuid4().hex[:4]
    logger = logging.Logger(logger_id)
    logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        # "%(asctime)s - %(levelname)s - %(message)s"
    )

    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if filepath:
        fh = logging.FileHandler(filepath, encoding="utf8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger
