from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageEvent, Message
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from utils.global_objects import group_manager
from utils.global_objects import plugin_manager
from utils.plugin_manager.plugin_status import PluginStatus
from nonebot import Bot
from utils.utils import get_group_name

add_group = on_command("添加群权限", aliases={"添加群认证", "添加群"}, permission=SUPERUSER, priority=5, block=True)
set_group_permission = on_command("设置群权限", permission=SUPERUSER, priority=5, block=True)


@add_group.handle()
async def _(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    if arg := arg.extract_plain_text().strip():
        if arg.lstrip('-').isdigit():
            group_id = arg
            if not group_manager.group_info.group_exist(group_id):
                group_manager.group_info.add_group(group_id, 2)
                plugin_manager.plugin_status._init_group(group_id)
                for plugin in plugin_manager.plugin_info.get_default_off_plugins():
                    plugin_manager.plugin_status.set_plugin_status(plugin, False, group_id)

            group_name = await get_group_name(bot, group_id)
            await add_group.finish(f"已添加群 {group_name}({group_id})")
        else:
            await add_group.finish("参数错误")
    else:
        await add_group.finish("参数错误")


@set_group_permission.handle()
async def _(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    if arg := arg.extract_plain_text().strip():
        arg = arg.split()
        if len(arg) == 2:  # 如果有两个参数
            permission = arg[0]
            group_id = arg[1]
            if permission.lstrip('-').isdigit():
                group_id = int(group_id)
                permission = int(permission)
                if not group_manager.group_info.group_exist(group_id):  # 插件管理器初始化
                    plugin_manager.plugin_status._init_group(group_id)
                if permission in [-1, 0, 1, 2]:
                    group_manager.group_info.set_group_permission(group_id, permission)
                    group_name = await get_group_name(bot, group_id)
                    await set_group_permission.finish(
                        f"已将群 {group_name}({group_id}) 的权限设置为 {permission}")
                else:
                    await set_group_permission.finish("权限只能是 -1, 0, 1, 2")
            else:
                await set_group_permission.finish("参数错误")
        elif len(arg) == 1:  # 如果只有一个参数
            if isinstance(event, GroupMessageEvent):
                if arg[0].lstrip('-').isdigit():
                    group_id = event.group_id
                    permission = int(arg[0])
                    group_manager.group_info.set_group_permission(group_id, permission)
                    await set_group_permission.finish(f"本群权限设置为 {permission}")
                else:
                    await set_group_permission.finish("参数错误")
            else:
                await set_group_permission.finish("参数错误")
    else:
        await set_group_permission.finish("参数错误")
