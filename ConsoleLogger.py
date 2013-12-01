import sys
import logging

def createLogger():
    logger = logging.getLogger(__file__)
    formatter = logging.Formatter(fmt='%(asctime)s; Level=%(levelname)s; Function=%(module)s::%(funcName)s:%(lineno)s; %(message)s')

    stdouthdlr = logging.StreamHandler(sys.stdout)
    stdouthdlr.setFormatter(formatter)
    logger.addHandler(stdouthdlr)

    logger.setLevel(logging.DEBUG)
    logger.info('Message="Logger has been initialized successfully"')
    return logger
