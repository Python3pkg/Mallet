#! /usr/bin/env python
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2014 Bartosz Janda
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import logging
import os


def get_logger():
    """
    Creates shared LLDB logger.
    """
    # Logger.
    logger = logging.getLogger("LLDBLogger")
    if not hasattr(logger, "configured"):
        logger.setLevel(logging.DEBUG)
        logger.configured = True

        # Formatter.
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s - %(message)s')

        # File handler.
        file_path = os.path.expanduser("~/Library/Logs/LLDBSummaries.log")
        file_handler = logging.FileHandler(file_path)
        file_handler.setFormatter(formatter)

        # Null handler.
        null_handler = logging.NullHandler()

        logger.addHandler(file_handler)
        # logger.addHandler(null_handler)
        logger.debug("LLDBLogger: logger created.")

    return logger