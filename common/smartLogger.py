#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import sys
# from logging.handlers import TimedRotatingFileHandler
import logging
import logging.handlers
import coloredlogs
LOG_FILE = "logs/modbus_sniffer.log"
# FORMAT = ('%(asctime)-15s %(threadName)-15s'
#       ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
FORMAT = (
    '%(asctime)s %(levelname)s [%(module)s.%(funcName)s:%(lineno)d] %(message)s')

def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(FORMAT))
    return console_handler


def get_file_handler():
    #file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
    # file_handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1000000, backupCount=3,)
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(FORMAT))
    return file_handler

def setup_logger(logger_name):
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(logger_name)
    coloredlogs.install(level=logging.DEBUG, logger=logger, fmt= FORMAT)
    # better to have too much log than not enough
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())
    # with this pattern, it's rarely necessary to propagate the error up to parent
    #logger.propagate = False
    return logger