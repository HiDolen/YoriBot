import nonebot
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, Bot
from nonebot.adapters.onebot.v11.permission import GROUP
from nonebot.adapters.onebot.v11.message import MessageSegment

from nonebot import on_regex, on_command, on_message
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="test",
    description="测试",
    usage="None",
    type="none",
    homepage="None",
    supported_adapters={"~onebot.v11"},
)


test = on_regex("test", priority=5, block=True, permission=GROUP,flags=0)
# test = on_message(priority=10, block=True, permission=GROUP)


@test.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await test.finish("test")
