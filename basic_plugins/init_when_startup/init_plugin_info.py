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
        
