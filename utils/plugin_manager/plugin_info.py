from pathlib import Path
from utils.static_data_io import StaticDataIO


class PluginInfo(StaticDataIO):
    """
    description:
        插件信息。只会存储配置过 __plugin_info__ 的插件
    """

    def __init__(self, path: Path):
        super().__init__(path)

    def plugin_exist(self, plugin: str):
        return plugin in self.data
    
    def get_all_plugin(self):
        """
        获取所有插件标识
        """
        return self.data.keys()
    
    def get_all_plugin_name(self):
        return [self.data[plugin]["plugin_name"] for plugin in self.data.keys()]
    
    def get_plugin_from_name(self, plugin_name: str):
        """
        从 插件名 获取 插件标识
        """
        for plugin in self.data.keys():
            if self.data[plugin]["plugin_name"] == plugin_name:
                return plugin
        return None
    
    def get_name_from_plugin(self, plugin: str):
        """
        从 插件标识 获取 插件名
        """
        if plugin in self.data.keys():
            return self.data[plugin]["plugin_name"]
        return None
    
    def remove_plugin(self, plugin: str):
        if plugin in self.data:
            del self.data[plugin]
            self.save()
    
    def get_default_off_plugins(self):
        """
        description:
            获取默认关闭的插件。即只返回 default_status 为 False 的插件
        """
        return [plugin for plugin in self.data.keys()
                if not self.data[plugin]["default_status"]]

    def set_plugin_info(self,
                        plugin: str,
                        *,
                        plugin_name: str,
                        description: str = None,
                        usage: str = None,
                        default_status: bool = True,
                        **kwargs):
        """
        description:
            用于添加、更新插件信息
        params:
            :param plugin: 插件。独一无二用于标识
            :param plugin_name: 插件名。插件设定的显示名称。应当也保证独一无二
            :param description: 插件描述
            :param usage: 插件使用方法
            :param default_status: 未设置群插件状态时，默认状态（针对新入群）
            :param kwargs: 其他参数
        """
        # 去除 usage 开头与结尾的空行
        usage = usage.strip()
        while usage.startswith("\n"):
            usage = usage[1:]
        while usage.endswith("\n"):
            usage = usage[:-1]
        self.data[plugin] = {
            "plugin_name": plugin_name,
            "description": description,
            "usage": usage,
            "default_status": default_status
        }
        for key in kwargs.keys():
            self.data[plugin][key] = kwargs[key]
        self.save()
    
    def info_is_different(self, plugin: str, info: dict):
        """
        description:
            检查插件信息是否有变化
        params:
            :param plugin: 插件
            :param info: 插件信息
        """
        if plugin not in self.data.keys():
            return True
        for key in info.keys():
            if self.data[plugin][key] != info[key]:
                return True
        return False
