from utils.group_manager import Group_Manager
from utils.plugin_manager import Plugin_Manager
import asyncio

import nonebot
from nonebot import require

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler as nonebot_scheduler


# 全局插件管理器
plugin_manager: Plugin_Manager = Plugin_Manager()
# 全局群组管理器
group_manager: Group_Manager = Group_Manager()


# 全局调度器，用于定时任务
scheduler = nonebot_scheduler
# 全局 bot 列表
bots: list = list(nonebot.get_bots().values())


async def init_with_async():
    pass

asyncio.get_event_loop().run_until_complete(init_with_async())
