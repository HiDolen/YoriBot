from pathlib import Path
from utils.static_data_io import StaticDataIO
from .path_config import image_dir, data_dir
from datetime import datetime


class WordBank(StaticDataIO):
    """
    词库。结构如下：

    {
        "group_id": {
            "key": [
                {
                    "setter_id": "123456",
                    "time": "2021-01-01",
                    "value": "回复内容",
                    "match_type": 0
                },
                ...
            ],
            ...
        },
        ...
    }
    """

    def __init__(self, path: Path):
        super().__init__(path)

    def add_a_key(
        self, group_id: str, setter_id: str, key: str, value: str, match_type: int
    ):
        """
        添加词条
        """
        if group_id not in self.data:
            self.data[group_id] = {}

        all_value = self.get_all_value_from_a_key(group_id, key)
        if value in [v["value"] for v in all_value]:
            return False

        piece = {
            "setter_id": setter_id,
            "time": datetime.now().strftime("%Y-%m-%d"),
            "value": value,
            "match_type": match_type,
        }

        if key in self.data[group_id]:
            self.data[group_id][key].insert(0, piece)
            # 将 data[group_id][key] 移动到 data[group_id] 的最后面
            self.data[group_id][key] = self.data[group_id].pop(key)
        else:
            self.data[group_id][key] = [piece]

        self.save()
        return True

    def delete_a_key(self, group_id: str, key: str):
        """
        删除词条
        """
        if group_id in self.data:
            if key in self.data[group_id]:
                del self.data[group_id][key]
                self.save()

    def delete_by_id(self, group_id: str, id: list[int]):
        """
        通过 id 删除词条 TODO 验证是否有 bug
        """
        # 遍历对应 group_id 的所有 value
        count = 0
        deleted = []
        for key in list(self.data[group_id].keys())[::-1]:
            if count in id:
                del self.data[group_id][key]
                deleted.append(count)
            count += 1
        self.save()
        return deleted

    def get_all_key(self, group_id: str):
        """
        获取所有词条
        """
        if group_id in self.data:
            return list(self.data[group_id].keys())
        return []

    def get_all_value_from_a_key(self, group_id: str, key: str):
        """
        获取某个词条的所有回复
        """
        if group_id in self.data:
            if key in self.data[group_id]:
                return self.data[group_id][key]
        return []

    def get_all_value_from_a_id(self, group_id: str, id: int):
        """
        通过 id 获取某个词条的所有回复
        """
        if group_id in self.data:
            if id < len(self.data[group_id].keys()):
                key = list(self.data[group_id].keys())[::-1][id]
                return self.data[group_id][key]
        return []

    def get_a_key_from_id(self, group_id: str, id: int):
        """
        通过 id 获取某个词条
        """
        if group_id in self.data:
            if id < len(self.data[group_id].keys()):
                return list(self.data[group_id].keys())[::-1][id]
        return ""


class Images(StaticDataIO):
    """
    description:
        维护现有的图片信息，不进行实际的图片存储管理
    """

    def __init__(self, path: Path):
        super().__init__(path)

    def add_a_image(self, name: str):
        """
        若没有该图片，则添加；若有，则 use_count + 1
        """
        if name in self.data:
            self.data[name]["use_count"] += 1
        else:
            self.data[name] = {"use_count": 1}
        self.save()

    def delete_a_image(self, name: str):
        """
        删除图片。若 use_count == 1，则删除，返回 True；否则 use_count - 1，返回 False
        """
        flag = False
        if name in self.data:
            if self.data[name]["use_count"] == 1:
                del self.data[name]
                flag = True
            else:
                self.data[name]["use_count"] -= 1
            self.save()
        return flag

    def get_all_name(self):
        return self.data.keys()


wordbank = WordBank(data_dir / "wordbank.json")
images = Images(data_dir / "images.json")
