import json
import os
from pathlib import Path
from utils.global_logger import logger
from ruamel.yaml import YAML
from ruamel import yaml
import copy

_yaml = YAML(typ="safe")


class StaticDataIO:
    """
    有的 manager 继承 StaticDataIO 实现静态数据存储
    """

    def __init__(self, path: Path):
        self.file_name = path.name

        self._path = path
        path.parent.mkdir(exist_ok=True, parents=True)  # 创建文件夹
        self._file_type = os.path.splitext(path)[1][1:]
        self.data: dict = {}

        self.reload()

    def set_root_value(self, root_key, value, save=True):
        self.data[root_key] = value
        if save:
            self.save()

    def set_level1_value(self, root_key, level1_key, value, save=True):
        """
        description:
            设置一级层级值
        params:
            :param root_key: 根键
            :param level1_key: 一级键
            :param value: 值
        """
        if root_key in self.data.keys():
            self.data[root_key][level1_key] = value
            if save:
                self.save()

    def get_root_value(self, root_key):
        return self.data.get(root_key)

    def get_keys(self):
        return self.data.keys()

    def delete_root_key(self, root_key, save=True):
        if root_key in self.data.keys():
            del self.data[root_key]
            if save:
                self.save()

    def get_all_data(self):
        return copy.deepcopy(self.data)

    def save(self):
        with open(self._path, "w", encoding="utf-8") as f:
            try:
                if self._file_type == "json":
                    json.dump(self.data, f, ensure_ascii=False, indent=4)
                elif self._file_type == "yaml":
                    yaml.dump(self.data, f)
            except Exception as e:
                logger.error(f"写入文件 {self._path} 失败：{e}")
                raise ValueError(f"写入文件 {self._path} 失败：{e}")

    def reload(self):
        if self._path.exists():
            with open(self._path, "r", encoding="utf-8") as f:
                try:
                    if self._file_type == "json":
                        self.data = json.load(f)
                    elif self._file_type == "yaml":
                        self.data = _yaml.load(f)
                except Exception as e:
                    logger.error(f"读取文件 {self._path} 失败：{e}")
                    raise ValueError(f"读取文件 {self._path} 失败：{e}")

    def is_file_exist(self):
        return self._path.exists()

    def is_data_empty(self):
        return self.data == {}

    def __setitem__(self, key, value):
        self.set_root_value(key, value)

    def __getitem__(self, key):
        return self.get_root_value(key)
