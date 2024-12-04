#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import logging

logger = None

class Logger:
    def __init__():
        pass
    
    @staticmethod
    def init(log_path=None):
        global logger
        
        if log_path is not None:
            logging.basicConfig(filename=log_path,
                                format="%(asctime)s %(message)s",
                                filemode="w")
        
        # Creating an object
        logger = logging.getLogger()
        
        # Setting the threshold of logger to DEBUG
        logger.setLevel(logging.INFO)

    @staticmethod
    def debug(msg):
        logger.debug(msg)
    
    @staticmethod
    def info(msg):
        logger.info(msg)
    
    @staticmethod
    def warning(msg):
        logger.warning(msg)
    
    @staticmethod
    def error(msg):
        logger.error(msg)

    @staticmethod
    def critical(msg):
        logger.critical(msg)


if __name__ == "__main__":
    Logger.init()
    Logger.debug("unit test: debug")
    Logger.info("unit test: info")
    Logger.warning("unit test: warning")
    Logger.error("unit test: error")
    Logger.critical("unit test: critical")
