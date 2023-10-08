# 管理群权限

from utils.static_data_io import StaticDataIO
from pathlib import Path
from configs.path_config import DATA_PATH


class Group_Manager:
    def __init__(self) -> None:
        path = DATA_PATH / "group_manager"
        self.group_info: GroupInfo = GroupInfo(path / "group_info.json")


class GroupInfo(StaticDataIO):
    """
    description:
        群信息
    """

    def __init__(self, path: Path):
        super().__init__(path)

    def add_group(self, group_id: str, permission: int = 0):
        """
        description:
            添加群
        params:
            :param group_id: 群号
            :param permission: 权限
（-1 为退群，0 为关闭功能，1 为认证，2 为允许群管理开关特权插件, 3 为允许群管理开关任意插件， 4 为允许任何人开关任意插件）
        """
        if not group_id in self.data:
            self.data[str(group_id)] = {
                "permission": permission
            }
            self.save()

    def remove_group(self, group_id: str):
        """
        description:
            移除群
        """
        if group_id in self.data:
            del self.data[str(group_id)]
            self.save()

    def group_exist(self, group_id: str):
        return str(group_id) in self.data
    
    def get_all_group(self):
        return self.data.keys()

    def get_group_permission(self, group_id: str):
        """
        description:
            获取群权限。如果群不存在，返回 -1
        """
        if not self.group_exist(group_id):
            return -1
        return self.data[str(group_id)]["permission"]

    def set_group_permission(self, group_id: str, permission: int):
        if not self.group_exist(group_id):
            self.add_group(group_id, permission)
        else:
            self.data[str(group_id)]["permission"] = permission
        self.save()
