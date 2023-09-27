import nonebot
import os

# 加载当前目录下的所有插件

path = __file__.rstrip(os.path.basename(__file__))
sub_dirs = []

for item in os.listdir(path):
    item_path = os.path.join(path, item)
    if os.path.isdir(item_path):
        nonebot.load_plugins(item)