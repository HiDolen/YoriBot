from loguru import logger as loguru_logger
from nonebot.log import default_format, default_filter
from datetime import datetime, timedelta
from configs.path_config import LOG_PATH

# 全局日志
logger = loguru_logger
logger.add(
    LOG_PATH / f'{datetime.now().strftime("%Y-%m-%d")}.log',
    level="INFO",
    rotation="00:00",
    filter=default_filter,
    enqueue=True,
    retention="7 days")
logger.add(
    LOG_PATH / f'error_{datetime.now().strftime("%Y-%m-%d")}.log',
    level="ERROR",
    rotation="00:00",
    filter=default_filter,
    enqueue=True,
    retention="7 days")