"""
日志工具 — 基于标准库 logging，输出到控制台和文件。
"""

import logging
import os
from datetime import datetime


def setup_logger(name: str = "ui-autotest",
                 log_dir: str = "logs") -> logging.Logger:
    """
    配置并返回 logger。

    - 控制台输出: INFO 级别，简洁格式
    - 文件输出:   DEBUG 级别，带时间戳和模块名

    Args:
        name:    logger 名称
        log_dir: 日志文件目录

    Returns:
        配置好的 Logger 实例
    """
    logger = logging.getLogger(name)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_fmt = logging.Formatter("[%(levelname)s] %(message)s")
    console_handler.setFormatter(console_fmt)

    # 文件 handler
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    file_handler = logging.FileHandler(
        os.path.join(log_dir, f"test_{timestamp}.log"),
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s | %(funcName)s:%(lineno)d — %(message)s"
    )
    file_handler.setFormatter(file_fmt)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# 模块级默认 logger
logger = setup_logger()
