from utils.global_objects import scheduler
from utils.global_logger import logger
from datetime import datetime
from utils.global_objects import plugin_manager
from nonebot.matcher import Matcher, matchers
import nonebot

# 每一周清理一次插件状态和信息
@scheduler.scheduled_job("cron", day_of_week="0", hour=1, minute=1, second=0)
async def clear_plugin_info_cron():
    logger.info("定时清理插件信息……")

    all_plugins = nonebot.plugin.get_loaded_plugins()
    all_plugins = [plugin.name for plugin in all_plugins]
    all_plugins_in_manager = plugin_manager.plugin_info.get_all_plugin()

    plugins_to_remove = set(all_plugins_in_manager) - set(all_plugins)
    for plugin in plugins_to_remove:
        plugin_manager.plugin_info.remove_plugin(plugin)
        plugin_manager.plugin_status.erase_plugin(plugin)

        logger.success(f"插件 {plugin} 信息已清理")

