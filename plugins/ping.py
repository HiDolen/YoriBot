import random
from datetime import date
from nonebot.plugin import on_keyword, on_regex
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.adapters.onebot.v11.message import Message
from nonebot.plugin import PluginMetadata
import nonebot

__plugin_meta__ = PluginMetadata(
    name="ping",
    description=r"回复 ping",
    usage="ping",
    type="debug",
    extra={
        "default_status": True
    }
)

command_start = nonebot.get_driver().config.command_start
command_start = '|'.join(command_start)

ping = on_regex(f'^({command_start})?(ping)$', priority=50)

@ping.handle()
async def ping_handle(bot: Bot, event: Event):
    await ping.finish(Message(f'pong'))