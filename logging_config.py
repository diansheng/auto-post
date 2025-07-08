# -*- coding: utf-8 -*-
"""
小红书自动发布工具的日志配置
"""

import os
import logging
from logging.handlers import RotatingFileHandler
import datetime

# 创建日志目录
LOG_DIR = 'logs'
os.makedirs(LOG_DIR, exist_ok=True)

# 生成日志文件名，包含日期
log_filename = os.path.join(LOG_DIR, f'rednote_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

# 配置根日志记录器
def setup_logger():
    # 创建日志记录器
    logger = logging.getLogger('rednote')
    logger.setLevel(logging.DEBUG)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    # 创建文件处理器
    file_handler = RotatingFileHandler(
        log_filename, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # 创建格式化器
    console_formatter = logging.Formatter('%(levelname)s: [%(filename)s:%(lineno)d] %(message)s')
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
    
    # 设置格式化器
    console_handler.setFormatter(console_formatter)
    file_handler.setFormatter(file_formatter)
    
    # 添加处理器到日志记录器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# 获取日志记录器实例
logger = setup_logger()