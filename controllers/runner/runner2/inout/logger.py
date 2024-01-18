import logging
import os
import sys

from inout.loader import configs

LOGGER_NAME: str = "online-mnw-robot-learning"
LOG_FORMAT: str = "[%(asctime)s %(levelname)s]\t %(message)s"
LOG_PATH: str = configs["output"]["path"]
LOG_FILE: str = configs["output"]["log_file"]

# obtain the logger instance
logger = logging.getLogger(LOGGER_NAME)

# calculate the log file position
file_path = os.path.join(LOG_PATH, LOG_FILE)

# define the file handler
handler = logging.FileHandler(file_path)
handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(handler)

# define the shell handler
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(handler)

# display all the logs
logger.setLevel(logging.DEBUG)

# export only the logger instance
__all__ = "logger",
