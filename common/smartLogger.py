#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import logging
import logging.handlers


def configure_handler():
    # Create handlers
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/modbus_sniffer.log', maxBytes=1000000, backupCount=3)
    # Set handler log level
    file_handler.setLevel(logging.DEBUG)
    # Create formatters
    # FORMAT = ('%(asctime)-15s %(threadName)-15s'
    #       ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
    frmt = ('%(asctime)s %(levelname)s [%(module)s.%(funcName)s:%(lineno)d] %(message)s')
    file_format = logging.Formatter(frmt)
    # Add formatter to the handler
    file_handler.setFormatter(file_format)

    return file_handler

