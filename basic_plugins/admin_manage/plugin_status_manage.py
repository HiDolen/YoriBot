from nonebot import on_command, Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageEvent, Message
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from utils.global_objects import plugin_manager as pm
from utils.global_objects import group_manager as gm
from utils.plugin_manager.plugin_status import PluginStatus
from nonebot.adapters import Event
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="插件管理",
    description="管理群插件开关、全局插件开关、特权插件等。全局禁用优先级最高。将插件添加到特权插件列表后，拥有群认证的群（群权限为 2 或以上）的管理员可以自由开关该插件。",
    usage="""
开启插件 今日人品
开启插件 今日人品 123456666

关闭插件 今日人品
关闭插件 今日人品 123456666

全局开启插件 今日人品
全局关闭插件 今日人品

（以下指令仅超级用户可用）

添加特权插件 今日人品
移除特权插件 今日人品
""",
    type="admin",
)

__force_to_operate__ = True


async def is_group_admin(bot: Bot, event: Event):
    user_id = event.get_user_id()
    if user_id in bot.config.superusers:
        return True
    if isinstance(event, GroupMessageEvent):
        group_id = str(event.group_id)
        permission = gm.group_info.get_group_permission(group_id)
        if permission <= 1:
            return False
        if permission >= 4:
            return True
        info = await bot.get_group_member_info(group_id=group_id, user_id=user_id)
        if info['role'] in ['owner', 'admin']:
            return True
    return False

activate_plugin_in_group = on_command("启用",
                                      aliases={"打开", "开启", "添加插件", "启用插件", "打开插件", "开启插件"},
                                      permission=is_group_admin,
                                      priority=2,
                                      block=True)

deactivate_plugin_in_group = on_command("禁用",
                                        aliases={"关闭", "禁用插件", "关闭插件"},
                                        permission=is_group_admin,
                                        priority=2,
                                        block=True)

activate_plugin_globally = on_command("全局启用",
                                      aliases={"全局打开", "全局开启"},
                                      permission=SUPERUSER,
                                      priority=2,
                                      block=True)

deactivate_plugin_globally = on_command("全局禁用",
                                        aliases={"全局关闭", "全局停用"},
                                        permission=SUPERUSER,
                                        priority=2,
                                        block=True)

add_privilege_plugin = on_command("添加特权插件",
                                  permission=SUPERUSER,
                                  priority=2,
                                  block=True)

remove_privilege_plugin = on_command("移除特权插件",
                                     aliases={"删除特权插件"},
                                     permission=SUPERUSER,
                                     priority=2,
                                     block=True)


@activate_plugin_in_group.handle()
async def _(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    arg = arg.extract_plain_text()
    # group_permission = gm.group_info.get_group_permission(str(event.group_id))
    if isinstance(event, GroupMessageEvent):
        group_permission = gm.group_info.get_group_permission(str(event.group_id))

        if plugin := pm.plugin_info.get_plugin_from_name(arg):
            is_super_user = event.get_user_id() in bot.config.superusers
            is_privilege = pm.plugin_status.is_privilege_plugin(
                plugin, str(event.group_id))
            if isinstance(event, GroupMessageEvent):
                if not is_privilege and not is_super_user and group_permission <= 2:
                    await activate_plugin_in_group.finish(f"参数错误")
                elif is_privilege or group_permission >= 3:
                    await activate_plugin_in_group.send(f"插件 {arg} 已启用")
                else:  # 不是特权插件，但超级用户
                    pm.plugin_status.add_privilege_plugin(plugin, str(event.group_id))
                    await activate_plugin_in_group.send(f"插件 {arg} 已启用，并且添加到特权插件列表")
                pm.plugin_status.set_plugin_status(
                    plugin, True, str(event.group_id))
    else:
        try:
            plugin_name, group_id = arg.split()
            group_permission = gm.group_info.get_group_permission(group_id)
            
            if plugin := pm.plugin_info.get_plugin_from_name(plugin_name):
                is_super_user = event.get_user_id() in bot.config.superusers
                is_privilege = pm.plugin_status.is_privilege_plugin(
                    plugin, str(event.group_id))
                group_name = await bot.get_group_info(group_id=group_id)['group_name']
                if not is_super_user:
                    await activate_plugin_in_group.finish(f"参数错误")
                if not is_privilege and group_permission <= 2:
                    pm.plugin_status.add_privilege_plugin(plugin, group_id)
                    await activate_plugin_in_group.send(
                        f"插件 {arg} 已在群 {group_name}({group_id}) 启用，并且添加到特权插件列表")
                else:
                    await activate_plugin_in_group.send(
                        f"插件 {arg} 已在群 {group_name}({group_id})")
                pm.plugin_status.set_plugin_status(
                    plugin, True, group_id)
        except:
            await activate_plugin_in_group.finish("参数错误")


@deactivate_plugin_in_group.handle()
async def _(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    arg = arg.extract_plain_text()
    if isinstance(event, GroupMessageEvent):
        if plugin := pm.plugin_info.get_plugin_from_name(arg):
            pm.plugin_status.set_plugin_status(
                plugin, False, str(event.group_id))
            await deactivate_plugin_in_group.finish(f"插件 {arg} 已关闭")
    else:
        try:
            plugin_name, group_id = arg.split()
            if plugin := pm.plugin_info.get_plugin_from_name(plugin_name):
                pm.plugin_status.set_plugin_status(
                    plugin, False, group_id)
                group_name = await bot.get_group_info(group_id=group_id)['group_name']
                await deactivate_plugin_in_group.finish(
                    f"插件 {arg} 已在群 {group_name}(id:{group_id}) 禁用")
        except:
            await deactivate_plugin_in_group.finish("参数错误")


@activate_plugin_globally.handle()
async def _(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    arg = arg.extract_plain_text()
    if plugin := pm.plugin_info.get_plugin_from_name(arg):
        pm.plugin_status.set_plugin_status(plugin, True)
        await activate_plugin_globally.finish(f"插件 {arg}({plugin}) 已全局启用")


@deactivate_plugin_globally.handle()
async def _(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    arg = arg.extract_plain_text()
    if plugin := pm.plugin_info.get_plugin_from_name(arg):
        pm.plugin_status.set_plugin_status(plugin, False)
        await deactivate_plugin_globally.finish(f"插件 {arg}({plugin}) 已全局禁用")


@add_privilege_plugin.handle()
async def _(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    if not event.get_user_id() in bot.config.superusers:
        return
    arg = arg.extract_plain_text()
    if plugin := pm.plugin_info.get_plugin_from_name(arg):
        if isinstance(event, GroupMessageEvent):
            pm.plugin_status.add_privilege_plugin(plugin, str(event.group_id))
            await add_privilege_plugin.finish(f"插件 {arg} 已添加到群的特权插件列表")
        else:
            try:
                plugin_name, group_id = arg.split()
                pm.plugin_status.add_privilege_plugin(plugin, group_id)
                group_name = await bot.get_group_info(group_id=group_id)['group_name']
                await add_privilege_plugin.finish(
                    f"插件 {arg} 已添加到群 {group_name}({group_id}) 的特权插件列表")
            except:
                await add_privilege_plugin.finish("参数错误")


@remove_privilege_plugin.handle()
async def _(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    if not event.get_user_id() in bot.config.superusers:
        return
    arg = arg.extract_plain_text()
    if plugin := pm.plugin_info.get_plugin_from_name(arg):
        if isinstance(event, GroupMessageEvent):
            pm.plugin_status.remove_privilege_plugin(plugin, str(event.group_id))
            await remove_privilege_plugin.finish(f"插件 {arg} 已从群的特权插件列表移除")
        else:
            try:
                plugin_name, group_id = arg.split()
                pm.plugin_status.remove_privilege_plugin(plugin, group_id)
                group_name = await bot.get_group_info(group_id=group_id)['group_name']
                await remove_privilege_plugin.finish(
                    f"插件 {arg} 已从群 {group_name}({group_id}) 的特权插件列表移除")
            except:
                await remove_privilege_plugin.finish("参数错误")
