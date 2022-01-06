import logging

NAME = 'online-mnw-robot-learning'
FORMAT = '[%(asctime)s %(levelname)s]\t %(message)s'


def set_logger(path: str) -> logging:
    default = logging.getLogger(NAME)

    formatter = logging.Formatter(FORMAT)

    handler = logging.FileHandler(path)
    handler.setFormatter(formatter)
    default.addHandler(handler)


logger = logging.getLogger(NAME)
