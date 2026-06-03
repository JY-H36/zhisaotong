import logging
import os
from utils.path_tools import get_abs_path
from datetime import datetime
#日志保存目录
LOG_ROOT = get_abs_path("logs")

#确保目录存在
os.makedirs(LOG_ROOT, exist_ok=True)

#日志格式配置
DEFAULT_LOG_FORMAT = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)

def get_logger(
        name:str="agent",
        console_level=logging.INFO,
        file_level=logging.DEBUG,
        log_file = None,
) -> logging.Logger:
    '''获取日志记录器'''
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # 设置最低日志级别为DEBUG

    if logger.handlers:
        return logger  # 如果已经配置了处理器，直接返回
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(console_handler)

    if not log_file:
        log_file = os.path.join(LOG_ROOT, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)

    logger.addHandler(file_handler)

    return logger

#快捷获取日志器
logger = get_logger()

if __name__ == "__main__":
    logger.debug("这是一个调试日志")
    logger.info("这是一个信息日志")
    logger.warning("这是一个警告日志")
    logger.error("这是一个错误日志")
    logger.critical("这是一个严重错误日志")
