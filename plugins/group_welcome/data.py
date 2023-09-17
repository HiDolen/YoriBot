from pathlib import Path
from utils.static_data_io import StaticDataIO
from .path_config import image_dir, data_dir
from datetime import datetime


class WelcomeMsg(StaticDataIO):
    """
    词库。结构如下：

    {
        "group_id": {
            "setter_id": "123456",
            "time": "2021-01-01",
            "msg": "回复内容",
        },
        ...
    }
    """

    def __init__(self, path: Path):
        super().__init__(path)

    def add_msg(self, group_id: str, setter_id: str, msg: str):
        piece = {
            "setter_id": setter_id,
            "time": datetime.now().strftime("%Y-%m-%d"),
            "msg": msg,
        }
        self.data[group_id] = piece
        self.save()
        return True

    def delete_msg(self, group_id: str):
        if group_id in self.data:
            del self.data[group_id]
            self.save()


    def get_msg(self, group_id: str):
        if group_id in self.data:
            return self.data[group_id]["msg"]
        return None


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


welcomeMsg = WelcomeMsg(data_dir / "welcomeMsg.json")
images = Images(data_dir / "images.json")
