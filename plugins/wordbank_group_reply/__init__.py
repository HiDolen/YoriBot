import re
from typing import Tuple, Any, Optional

from nonebot.internal.params import Arg, ArgStr
from nonebot.typing import T_State

from nonebot.params import CommandArg, RegexGroup, Command
from nonebot.exception import FinishedException
from configs.path_config import DATA_PATH
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, unescape
from nonebot.adapters.onebot.v11.permission import (
    GROUP_ADMIN,
    GROUP_OWNER,
)
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot import on_command, on_regex, on_message
from nonebot.plugin import PluginMetadata
import nonebot
import random
from utils.image_utils.image_builder import ImageBuilder_Text, ImageBuilder
from .types import MatchType

# from .database import WordBank, Images
from .data import wordbank, images
from .utils import *

__plugin_meta__ = PluginMetadata(
    name="群词条",
    description=r"词库群回复，自定义词库回复",
    usage="""
添加词条 模糊 问...答...（关键词触发）
添加词条 问...答...（全匹配触发）
添加词条 模糊 #...#...
添加词条 #...#...

删除词条 一个问句（通过问句删除）
删除词条 0 4 5 6 11（通过 id 删除）

查看所有词条
显示所有词条
查看词条 一个问句（通过问句查看）
显示词条 一个问句
查看词条 0（通过 id 查看）
显示词条 0

编写问句时，可使用的标识：
    [at bot]：at 机器人
    [at]：at 任意某个人
    [at 123456]：at 那个 qq 号是 123456 的人
    
编写答句时，可使用的标识：
    [at self]：at 触发回复的人
    [at 123456]：at 那个 qq 号是 123456 的人（也支持在回答中直接 at，bot能够识别出来）
    [name self]：触发回复的人的昵称
    """, # TODO 编写 [at bot] 和 [at] 的匹配
    type="application",
    supported_adapters={"~onebot.v11"},
)


PERM_EDIT = GROUP_ADMIN | GROUP_OWNER | SUPERUSER

########################################################################################

command_start = nonebot.get_driver().config.command_start

add_aliases = {"添加回复", "增加回复", "添加词条", "增加词条", "添加问句", "增加问句"}
flags_include = ["关键词", "关键词匹配", "模糊", "模糊匹配"]
regex_parts = [
    r"^" + f"(?:{'|'.join(command_start)})(?:{'|'.join(add_aliases)})",  # 匹配指令
    r"[^\S]?(?:\s?)*" + f"((?:{'|'.join(flags_include)}))?" + r"[^\S]*",  # 获得 flag
    r"\s*(\S+.*?)[^\S]*",  # 获得 key
    r"\s*(\S+.*?)\s*$",  # 获得 value
]
regex_string = (
    regex_parts[0]
    + regex_parts[1]
    + "(?:#|问)"
    + regex_parts[2]
    + "(?:#|答)"
    + regex_parts[3]
)

add = on_regex(
    regex_string,
    flags=re.S,
    block=True,
    priority=10,
    permission=PERM_EDIT,
)


@add.handle()
async def _(bot: Bot, event: GroupMessageEvent, matched=RegexGroup()):
    flag, key, value = matched
    key, value = Message(key), Message(value)  # str 还原成 Message 类型
    flag = MatchType.include if flag in flags_include else MatchType.congruence
    if "image" in [m.type for m in key]:
        await add.finish("触发字段不支持图片")

    key = message2value(key)
    await save_image(value)
    value = message2value(value)

    group_id = str(event.group_id)
    if wordbank.add_a_key(group_id, str(event.user_id), key, value, flag.value):
        await add.finish(f"已添加词条：{key[:12]}{'...' if len(key) > 12 else ''}")
    else:
        await add.finish("词条已存在")


########################################################################################

delete = on_command(
    "删除词条",
    aliases={"删除群词条", "删除问句"},
    priority=5,
    block=True,
)


@delete.handle()
async def _(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    group_id = str(event.group_id)
    arg = message2value(arg)
    if arg in wordbank.get_all_key(group_id):
        for value in wordbank.get_all_value_from_a_key(group_id, arg):
            delete_image(value["value"])
        wordbank.delete_a_key(group_id, arg)
        await delete.finish(f"已删除词条：{arg[:12]}{'...' if len(arg) > 12 else ''}")
    elif re.match(r"^\d+(?:\s+\d+)*$", arg):
        ids = [int(i) for i in arg.split()]
        for id in ids:
            for value in wordbank.get_all_value_from_a_id(group_id, id):
                delete_image(value["value"])
        deleted = wordbank.delete_by_id(group_id, ids)
        deleted = [str(i) for i in deleted]
        await delete.finish(f"已删除词条：{', '.join(deleted)}\n现在词条序号可能有所变化")
    else:
        await delete.finish("没有该词条")


########################################################################################

c_1 = ["查看", "显示", "查询", "查看所有", "显示所有", "查询所有"]
c_2 = ["词条", "词库", "问句", "群词条", "群词库"]
c = [i + j for i in c_1 for j in c_2]

show_all = on_command(
    c[0],
    aliases=set(c[1:]),
    priority=5,
    block=True,
)


@show_all.handle()
async def _(bot: Bot, event: GroupMessageEvent, arg: Message = CommandArg()):
    width = 640  # 整张图的宽度
    spacing = 4  # 字间距
    font_args = {  # 用于生成图片
        "font": "msyh.ttf",
        "font_size": 30,
        "color": (0, 0, 0, 255),
    }
    font_args_mini = {
        "font": "msyh.ttf",
        "font_size": 16,
        "color": (0, 0, 0, 255),
    }

    group_id = str(event.group_id)
    all_key = wordbank.get_all_key(group_id)[::-1]
    if len(all_key) == 0:
        await show_all.finish("当前群没有词条")

    arg = message2value(arg)

    if "所有" in event.get_plaintext() or arg == "":
        img_header: ImageBuilder_Text = ImageBuilder_Text(f"本群词条", **font_args)
        img_header.extend_to_size(w=width)
        count = -1
        for key in all_key:
            count += 1
            key = truncate_str(key, 20)
            value = wordbank.get_all_value_from_a_key(group_id, key)[:3]
            value = [truncate_str(v["value"], 20) for v in value]
            if len(value) == 3:
                value[2] = "..."
            img_key = ImageBuilder_Text(
                f"{count}. " + key, warp_width=580, warp_spacing=4, **font_args
            )
            img_value = [
                ImageBuilder_Text(v, warp_width=500, warp_spacing=4, **font_args)
                for v in value
            ]
            img_header.join_image_vertical(img_key, align="right", spacing=spacing)
            for v in img_value:
                img_header.join_image_vertical(v, align="right", spacing=spacing)
    elif values := (
        wordbank.get_all_value_from_a_key(group_id, arg)
        or wordbank.get_all_value_from_a_id(group_id, int(arg))
    ):
        arg = wordbank.get_a_key_from_id(group_id, int(arg)) or arg
        img_header: ImageBuilder_Text = ImageBuilder_Text(f"词条：{arg}", **font_args)
        img_header.extend_to_size(w=width)
        for value in values:
            img_info = (
                "" if value["match_type"] == MatchType.congruence.value else "模糊匹配"
            )
            img_info += f"（id：{value['setter_id']}, time：{value['time']}）"
            img_info = ImageBuilder_Text(
                img_info, warp_width=540, warp_spacing=4, **font_args_mini
            )
            img_value = ImageBuilder_Text(
                value["value"], warp_width=540, warp_spacing=4, **font_args
            )
            img_header.join_image_vertical(img_info, align="right", spacing=spacing)
            img_header.join_image_vertical(img_value, align="right", spacing=spacing)
    else:
        await show_all.finish("没有该词条")

    img_header.pure_color_background()
    await show_all.finish(MessageSegment.image(img_header.get_byte_png()))


########################################################################################


def match_rule(event: GroupMessageEvent, state: T_State) -> bool:
    group_id = str(event.group_id)
    if values := match_from_message(event.message, group_id):
        value = random.choice(values)
        value = value2message(value, event)
        state["reply"] = value
        return True
    return False


handler = on_message(match_rule, priority=99)


@handler.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    reply = state["reply"]
    await handler.finish(reply)

