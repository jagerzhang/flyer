# -*- coding: utf-8 -*-
"""
日志文件配置
https://github.com/tiangolo/fastapi/issues/81#issuecomment-473677039
"""

import os
import sys
from loguru import logger
from utils.common import CommonFunc

common_func = CommonFunc()


def log_init(file_log_level, console_log_level):
    """初始化日志配置
    """
    basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 定位到log日志文件
    log_path = os.path.join(basedir, "logs")

    if not os.path.exists(log_path):
        os.mkdir(log_path)

    log_path_file = os.path.join(log_path, "flyer.log")
    # 日志简单配置
    logger.remove()
    logger.add(log_path_file,
               rotation="00:00",
               retention="30 days",
               enqueue=True,
               level=file_log_level)
    logger.add(sys.stderr, level=console_log_level)
    return logger
