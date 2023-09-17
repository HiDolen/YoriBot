import re
from typing import Tuple, Any, Optional

from nonebot.internal.params import Arg, ArgStr
from nonebot.typing import T_State

from nonebot.params import CommandArg, RegexGroup, Command
from nonebot.exception import FinishedException
from configs.path_config import DATA_PATH
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    unescape,
    GroupIncreaseNoticeEvent,
)
from nonebot.adapters.onebot.v11.permission import GROUP
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot import on_command, on_regex, on_message, on_notice
from nonebot.plugin import PluginMetadata
import nonebot
import random
from utils.image_utils.image_builder import ImageBuilder_Text, ImageBuilder

from .data import welcomeMsg, images
from .utils import *

__plugin_meta__ = PluginMetadata(
    name="进群欢迎",
    description=r"自定义新人入群时的欢迎语",
    usage="""
    自定义进群欢迎消息 balabalabala...
    设置群欢迎消息 balabalabala...

    查看群欢迎消息
    群欢迎消息

    删除群欢迎消息

    编写欢迎消息，可使用的标识：
        [at]：at 进群的人
    """,
    type="application",
    supported_adapters={"~onebot.v11"},
    extra={
        "default_status": True
    }
)

set_welcome = on_command(
    "自定义进群欢迎消息",
    aliases={"自定义欢迎消息", "自定义群欢迎消息", "设置群欢迎消息"},
    permission=GROUP,
    priority=5,
    block=True,
)


@set_welcome.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    await save_image(arg)
    msg = message2string(arg)
    group_id = str(event.group_id)
    setter_id = str(event.user_id)
    welcomeMsg.add_msg(group_id, setter_id, msg)
    await set_welcome.finish("欢迎消息设置成功")


########################################################################################

view_welcome = on_command(
    "群欢迎消息",
    aliases={"查看群欢迎消息", "查看当前群欢迎消息", "查看欢迎消息"},
    permission=GROUP,
    priority=5,
    block=True,
)


@view_welcome.handle()
async def _(event: GroupMessageEvent):
    group_id = str(event.group_id)
    msg = welcomeMsg.get_msg(group_id)
    if not msg:
        await view_welcome.finish("当前没有设置欢迎消息")
    msg = string2message(msg)


########################################################################################

delete_welcome = on_command(
    "删除群欢迎消息",
    aliases={"删除欢迎消息"},
    permission=GROUP,
    priority=5,
    block=True,
)

@delete_welcome.handle()
async def _(event: GroupMessageEvent):
    group_id = str(event.group_id)
    welcomeMsg.delete_msg(group_id)
    await delete_welcome.finish("欢迎消息删除成功")


########################################################################################

send_welcome = on_notice(priority=1, block=False)


@send_welcome.handle()
async def _(bot: Bot, event: GroupIncreaseNoticeEvent):
    group_id = str(event.group_id)
    user_id = str(event.user_id)
    if msg := welcomeMsg.get_msg(group_id):
        msg = string2message(msg)
        send_welcome.finish(msg)
