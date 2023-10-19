from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageEvent, Message
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from utils.global_objects import group_manager
from utils.global_objects import plugin_manager
from utils.plugin_manager.plugin_status import PluginStatus
from nonebot import Bot
from utils.utils import get_group_name
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="群权限管理",
    description="管理群权限、群认证",
    usage="""
添加群认证
添加群认证 123456666

移除群认证
移除群认证 123456666

设置群权限 2
设置群权限 123456666 2
""",
    type="admin",
)

__force_to_operate__ = True

add_group = on_command("添加群权限", aliases={"添加群认证"}, permission=SUPERUSER, priority=5, block=True)
remove_group = on_command("移除群权限", aliases={"移除群认证", "删除群权限", "删除群认证"}, permission=SUPERUSER, priority=5, block=True)
set_group_permission = on_command("设置群权限", permission=SUPERUSER, priority=5, block=True)


@add_group.handle()
async def _(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    if isinstance(event, GroupMessageEvent):
        group_id = str(event.group_id)
    elif arg := arg.extract_plain_text().strip():
        if arg.lstrip(' ').isdigit():
            group_id = arg
        else:
            await add_group.finish("参数错误")
    else:
        await add_group.finish("参数错误")

    if not group_manager.group_info.group_exist(group_id):
        group_manager.group_info.add_group(group_id, 2)
        plugin_manager.plugin_status._init_group(group_id)
        for plugin in plugin_manager.plugin_info.get_default_off_plugins():
            plugin_manager.plugin_status.set_plugin_status(plugin, False, group_id)

        group_name = await get_group_name(bot, group_id)
        await add_group.finish(f"已添加群 {group_name}({group_id})")
    else:
        await add_group.finish("群已存在")

@remove_group.handle()
async def _(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    if isinstance(event, GroupMessageEvent):
        group_id = str(event.group_id)
    elif arg := arg.extract_plain_text().strip():
        if arg.lstrip(' ').isdigit():
            group_id = arg
        else:
            await remove_group.finish("参数错误")
    else:
        await remove_group.finish("参数错误")

    if group_manager.group_info.group_exist(group_id):
        group_manager.group_info.remove_group(group_id)
        group_name = await get_group_name(bot, group_id)
        await remove_group.finish(f"已移除群 {group_name}({group_id})")
    else:
        await remove_group.finish("群不存在")


@set_group_permission.handle()
async def _(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    if arg := arg.extract_plain_text().strip():
        arg = arg.split()
        if len(arg) == 2:  # 如果有两个参数
            group_id = arg[0].lstrip(' ')
            permission = arg[1].lstrip(' ')
            if permission.isdigit():
                permission = int(permission)
                if permission in [-1, 0, 1, 2, 3, 4]:
                    group_manager.group_info.set_group_permission(group_id, permission)
                    group_name = await get_group_name(bot, group_id)
                else:
                    await set_group_permission.finish("权限只能是 -1, 0, 1, 2, 3, 4")
                # group_id = int(group_id)
                if not group_manager.group_info.group_exist(group_id):  # 插件管理器初始化
                    plugin_manager.plugin_status._init_group(group_id)
                    for plugin in plugin_manager.plugin_info.get_default_off_plugins():
                        plugin_manager.plugin_status.set_plugin_status(plugin, False, group_id)
                await set_group_permission.finish(
                    f"已将群 {group_name}({group_id}) 的权限设置为 {permission}")
            else:
                await set_group_permission.finish("参数错误")
        elif len(arg) == 1:  # 如果只有一个参数
            if not isinstance(event, GroupMessageEvent):
                await set_group_permission.finish("参数错误")

            permission = arg[0].lstrip(' ')
            if permission.isdigit():
                permission = int(permission)
                group_id = str(event.group_id)
                if permission in [-1, 0, 1, 2, 3, 4]:
                    group_manager.group_info.set_group_permission(group_id, permission)
                    group_name = await get_group_name(bot, group_id)
                else:
                    await set_group_permission.finish("权限只能是 -1, 0, 1, 2, 3, 4")
            else:
                await set_group_permission.finish("参数错误")
            await set_group_permission.finish(f"本群权限设置为 {permission}")
        else:
            await set_group_permission.finish("参数错误")
    else:
        await set_group_permission.finish("参数错误")
