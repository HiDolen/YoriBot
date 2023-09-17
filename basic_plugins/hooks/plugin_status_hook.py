from utils.global_objects import plugin_manager, group_manager
from utils.plugin_manager.plugin_status import PluginStatus
from nonebot.message import run_preprocessor, IgnoredException
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import (
    Bot,
    ActionFailed,
    MessageEvent,
    GroupMessageEvent,
    PokeNotifyEvent,
    PrivateMessageEvent,
    Message,
    Event,
)
from nonebot.typing import T_State

"""
处理事件之前，检查插件是否被禁用
"""


@run_preprocessor
async def _(matcher: Matcher, bot: Bot, event: Event, state: T_State):
    if event.get_user_id() in bot.config.superusers:
        return
    
    if hasattr(matcher.plugin.module, "__force_to_operate__"):
        if matcher.plugin.module.__force_to_operate__:
            return

    plugin = matcher.plugin_name
    status_manager: PluginStatus = plugin_manager.plugin_status
    plugin_name = plugin_manager.plugin_info.get_name_from_plugin(plugin)

    user_id = event.get_user_id()
    group_id = None
    if isinstance(event, GroupMessageEvent):
        group_id = str(event.group_id)
    if status_manager.get_plugin_status(plugin, group_id):
        if group_manager.group_info.get_group_permission(group_id) >= 1:
            return

    if group_id:
        raise IgnoredException(
            f"忽略用户 {user_id} 在群 {group_id} 对插件 {plugin_name} 的调用")
    else:
        raise IgnoredException(
            f"忽略私聊用户 {user_id} 对插件 {plugin_name} 的调用")
