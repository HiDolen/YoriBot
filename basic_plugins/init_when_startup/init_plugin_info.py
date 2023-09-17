import nonebot
from nonebot import Driver
from utils.global_objects import plugin_manager
from utils.global_logger import logger
from nonebot.matcher import Matcher, matchers

driver: Driver = nonebot.get_driver()


@driver.on_startup
async def _():
    all_matchers = []
    for i in matchers.keys():
        for matcher in matchers[i]:
            if matcher not in all_matchers:
                all_matchers.append(matcher)

    plugin_set = nonebot.plugin.get_loaded_plugins()
    for plugin in plugin_set:
        name = plugin.name
        # 判断是否有 __plugin_meta__ 属性
        if plugin.metadata != None:
            try:
                metadata = plugin.metadata
                metadata_extra = plugin.metadata.extra
                info = {
                    "plugin_name": metadata.name if metadata.name else None,
                    "description": metadata.description if metadata.description else None,
                    "usage": metadata.usage if metadata.usage else None,
                    "default_status": metadata_extra["default_status"] if "default_status" in metadata_extra else True,
                }
                if plugin_manager.plugin_info.info_is_different(name, info):
                    plugin_manager.plugin_info.set_plugin_info(name, **info)
                    logger.success(f"插件 `{plugin.metadata.name}({name})` 信息更新")
            except AttributeError:
                logger.warning(f"插件 {name} 未正确设置 __plugin_meta__")
        else:
            continue

    # TODO 删除已经不存在的插件信息。也就是垃圾清理环节
        

    # for matcher in all_matchers:
    #     matcher: Matcher = matcher
    #     try:
    #         module = matcher.plugin.module
    #     except AttributeError:
    #         continue

    #     try:
    #         plugin_info = module.__getattribute__("__plugin_info__")
    #         plugin = matcher.plugin_name
    #         try:
    #             info = {
    #                 "plugin_name": plugin_info["plugin_name"],
    #                 "description": plugin_info["description"],
    #                 "usage": plugin_info["usage"],
    #                 "default_status": plugin_info["default_status"]
    #             }
    #             if plugin_manager.plugin_info.info_is_different(plugin, info):
    #                 plugin_manager.plugin_info.set_plugin_info(plugin, **info)
    #                 logger.info(f"插件 `{plugin_info['plugin_name']}({plugin})` 信息更新")
    #         except AttributeError:
    #             logger.warning(f"插件 {plugin} 未正确设置 __plugin_info__")
    #     except AttributeError:
    #         pass

    all_plugins = [
        matcher.plugin.name for matcher in all_matchers if matcher.plugin]
    all_plugins_in_manager = plugin_manager.plugin_info.get_all_plugin()
    # 删除已经不存在的插件
    plugins_to_delete = set(all_plugins_in_manager) - set(all_plugins)
    for plugin in plugins_to_delete:
        plugin_manager.plugin_info.remove_plugin(plugin)
        logger.success(f"插件 {plugin} 信息已删除")
