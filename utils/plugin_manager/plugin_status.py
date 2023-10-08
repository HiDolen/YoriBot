from pathlib import Path
from utils.static_data_io import StaticDataIO


class PluginStatus(StaticDataIO):
    """
    管理插件在群中的状态。
    包括：全局禁用插件、群禁用插件、群启用的被动
    """

    def __init__(self, path: Path):
        super().__init__(path)
        if not self.data:
            self.data = {
                "global_closed_plugins": [],
                "group_plugin_status": {},
                "private_closed_plugins": []
            }
            self.save()

    def get_plugin_status(self, plugin: str, group_id: str = None):
        """
        description:
            获取插件状态。全局禁用优先级更高。若群不存在，则返回 False
        params:
            :param plugin: 插件
            :param group_id: 群号。为空则为私聊
        """

        # 若是全局禁用
        if plugin in self.data["global_closed_plugins"]:
            return False

        if group_id:
            # 若未设置群
            if group_id not in self.data["group_plugin_status"].keys():
                return False
            # 若群已禁用插件
            if plugin in self.data["group_plugin_status"][group_id]["closed_plugins"]:
                return False
        else:
            if plugin in self.data["private_closed_plugins"]:
                return False
        return True

    def set_plugin_status(self, plugin: str, status: bool, group_id: str = None):
        """
        description:
            设置插件状态
        params:
            :param plugin: 插件
            :param status: 状态
            :param group_id: 群号。为空则为全局设置
        """
        if group_id:
            self._init_group(group_id)
            if status:
                if plugin in self.data["group_plugin_status"][group_id]["closed_plugins"]:
                    self.data["group_plugin_status"][group_id]["closed_plugins"].remove(plugin)
            else:
                if not plugin in self.data["group_plugin_status"][group_id]["closed_plugins"]:
                    self.data["group_plugin_status"][group_id]["closed_plugins"].append(plugin)
        else:
            if status:
                if plugin in self.data["global_closed_plugins"]:
                    self.data["global_closed_plugins"].remove(plugin)
            else:
                if not plugin in self.data["global_closed_plugins"]:
                    self.data["global_closed_plugins"].append(plugin)
        self.save()

    def set_plugin_status_private(self, plugin: str, status: bool):
        """
        description:
            设置私聊下的插件状态
        params:
            :param plugin: 插件
            :param status: 状态
        """
        if status:
            if plugin in self.data["private_closed_plugins"]:
                self.data["private_closed_plugins"].remove(plugin)
        else:
            if not plugin in self.data["private_closed_plugins"]:
                self.data["private_closed_plugins"].append(plugin)
        self.save()

    def add_privilege_plugin(self, plugin: str, group_id: str):
        """
        description:
            添加群管理所允许开启的插件
        params:
            :param plugin: 插件
            :param group_id: 群号
        """
        self._init_group(group_id)
        if not plugin in self.data["group_plugin_status"][group_id]["privilege_plugins"]:
            self.data["group_plugin_status"][group_id]["privilege_plugins"].append(plugin)
            self.save()
    
    def remove_privilege_plugin(self, plugin: str, group_id: str):
        """
        description:
            移除群管理所允许开启的插件
        params:
            :param plugin: 插件
            :param group_id: 群号
        """
        self._init_group(group_id)
        if plugin in self.data["group_plugin_status"][group_id]["privilege_plugins"]:
            self.data["group_plugin_status"][group_id]["privilege_plugins"].remove(plugin)
            self.save()

    def is_privilege_plugin(self, plugin: str, group_id: str):
        """
        description:
            判断插件是否为特权插件
        params:
            :param plugin: 插件
            :param group_id: 群号
        """
        self._init_group(group_id)
        return plugin in self.data["group_plugin_status"][group_id]["privilege_plugins"]

    def _init_group(self, group_id: str):
        """
        description:
            初始化群插件数据。仅新建群数据，不包括初始化插件的开关状态
        params:
            :param group_id: 群号
        """
        if not group_id in self.data["group_plugin_status"].keys():
            self.data["group_plugin_status"][group_id] = {
                "closed_plugins": [], # 群禁用的插件。可由群管理员修改
                "privilege_plugins": [], # 群管理所允许开启的插件
            }
