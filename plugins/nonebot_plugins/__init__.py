import nonebot
import os

# 加载当前目录下的所有插件

path = __file__.rstrip(os.path.basename(__file__))

for item in os.listdir(path):
    item_path = os.path.join(path, item)
    if not os.path.isdir(item_path):
        continue
    for sub_item in os.listdir(item_path):
        sub_item_path = os.path.join(item_path, sub_item)
        if not os.path.isdir(sub_item_path):
            continue
        if item == sub_item:
            nonebot.load_plugins(item_path)