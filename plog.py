#coding=utf-8# -*- coding: UTF-8 -*-
import os
curdir = os.path.dirname(__file__)
import sys
sys.path.append(curdir)
import logging,time

def get_logger(logfile, loglevel):
        """Return a logger named class.name.
        if logfile is None, it will output to console.
        if loglevel is an integer of [1,5], more details if larger.
        """
        logger = logging.getLogger(__name__)
        if not logfile:
            log_handler = logging.StreamHandler()
        else:
            log_handler = logging.FileHandler(logfile)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_handler.setFormatter(formatter)
        ll = (logging.CRITICAL,
              logging.ERROR,
              logging.WARNING,
              logging.INFO,
              logging.DEBUG)
        if not loglevel in range(1, 6):
            loglevel = 5
        logger.setLevel(ll[loglevel - 1])
        log_handler.setLevel(ll[loglevel - 1])
        logger.addHandler(log_handler)
        return logger

logger = get_logger(os.path.join(curdir,'phishing.log') , 5)

def plog(mess):
    logger.info(mess)

