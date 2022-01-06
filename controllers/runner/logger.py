import logging

FORMAT = '[%(asctime)s %(levelname)s]\t %(message)s'

logger = logging.getLogger('online-mnw-robot-learning')

formatter = logging.Formatter(FORMAT)

fileHandler = logging.FileHandler('log')
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
