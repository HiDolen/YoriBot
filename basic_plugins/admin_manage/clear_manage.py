from utils.global_objects import scheduler
from utils.global_logger import logger
from configs.path_config import TEMP_PATH
from datetime import datetime
from nonebot import on_command, Bot
from nonebot.permission import SUPERUSER
from utils.global_objects import plugin_manager, group_manager
import nonebot
import os
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="清理管理",
    description="清理多余的插件信息、多余群的信息。",
    usage="""
清理冗余插件信息
清理冗余群信息
清理冗余信息
""",
    type="admin",
)


__force_to_operate__ = True

clear_plugin_info = on_command("清理冗余插件信息", permission=SUPERUSER, priority=2, block=True)
clear_group_info = on_command("清理冗余群信息", permission=SUPERUSER, priority=2, block=True)
clear_all_info = on_command("清理冗余信息", permission=SUPERUSER, priority=2, block=True)

def erase_plugin_info():
    all_plugins = nonebot.plugin.get_loaded_plugins()
    all_plugins = [plugin.name for plugin in all_plugins]
    all_plugins_in_manager = plugin_manager.plugin_info.get_all_plugin()

    plugins_to_remove = set(all_plugins_in_manager) - set(all_plugins)
    for plugin in plugins_to_remove:
        plugin_manager.plugin_info.remove_plugin(plugin)
        plugin_manager.plugin_status.erase_plugin(plugin)
        logger.success(f"插件 {plugin} 信息已清理")

    return plugins_to_remove

def erase_group_info(all_groups):
    all_groups_in_manager = group_manager.group_info.get_all_group()

    groups_to_remove = set(all_groups_in_manager) - set(all_groups)
    for group in groups_to_remove:
        group_manager.group_info.remove_group(group)
        plugin_manager.plugin_status.erase_group(group)
        logger.success(f"群 {group} 信息已清理")

    return groups_to_remove

@clear_plugin_info.handle()
async def _(bot: Bot):
    logger.info("超级用户主动清理冗余插件信息……")
    plugins_to_remove = erase_plugin_info()
    await clear_plugin_info.finish(f"插件信息清理完毕。共清理了 {len(plugins_to_remove)} 个插件。")

@clear_group_info.handle()
async def _(bot: Bot):
    # 清理未加入的群的信息
    logger.info("超级用户主动清理冗余群信息……")
    group_list = await bot.get_group_list()
    all_groups = [str(group['group_id']) for group in group_list]
    groups_to_remove = erase_group_info(all_groups)
    await clear_group_info.finish(f"群信息清理完毕。共清理了 {len(groups_to_remove)} 个群。")

@clear_all_info.handle()
async def _(bot: Bot):
    logger.info("超级用户主动清理冗余信息……")

    plugins_to_remove = erase_plugin_info()
    group_list = await bot.get_group_list()

    all_groups = [str(group['group_id']) for group in group_list]
    groups_to_remove = erase_group_info(all_groups)
    
    await clear_all_info.finish(f"信息清理完毕。共清理了 {len(plugins_to_remove)} 个插件，{len(groups_to_remove)} 个群。")

    

