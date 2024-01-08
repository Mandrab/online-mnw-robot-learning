import dataclasses
import logging
import os
import sys

NAME = 'online-mnw-robot-learning'


@dataclasses.dataclass
class Settings(logging.Logger):
    """
    Contains the settings for the logger. To guarantee their application, the
    settings have to be committed through the 'setup' function.

    Parameters:
     - path: where to save the log file and the logging plots. It's a folder path
     - log_file: the name of the log file in the path folder
     - log_format: the format of the logging from the application
    """

    path: str = ''

    log_file: str = '../../log'
    log_format: str = '[%(asctime)s %(levelname)s]\t %(message)s'


def setup(instance: logging.Logger, settings: Settings):
    """
    Set an output file and console for the logs. The file is specified by the
    logging settings. Moreover, set the logging style/format.

    :parameter instance: of the logger to set
    :parameter settings: settings to apply to the logger
    """
    file_path = os.path.join(settings.path, settings.log_file)

    # file handler
    handler = logging.FileHandler(file_path)
    handler.setFormatter(logging.Formatter(settings.log_format))
    instance.addHandler(handler)

    # shell handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(settings.log_format))
    instance.addHandler(handler)

    # display all the logs
    instance.setLevel(logging.DEBUG)


logger = logging.getLogger(NAME)
