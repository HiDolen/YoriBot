from utils.global_objects import scheduler
from utils.global_logger import logger
from configs.path_config import TEMP_PATH
from datetime import datetime
import os

@scheduler.scheduled_job("cron", hour="1, 13", minute=1, second=0)
async def clear_temp_file_cron():
    # 清理时间超过 1 天的临时文件
    logger.info("定时清理临时文件……")
    count = 0
    total_size = 0
    for file in TEMP_PATH.iterdir():
        if file.is_file():
            if (datetime.now() - datetime.fromtimestamp(file.stat().st_mtime)).days > 1:
                total_size += os.path.getsize(file)
                file.unlink()
                count += 1
    logger.success(f"清理了 {count} 个临时文件，共 {total_size / 1024 / 1024:.2f} MB")
