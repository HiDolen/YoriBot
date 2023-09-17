import os
right_path = __file__.rstrip(os.path.basename(__file__))    # 获取当前文件的所在路径
os.chdir(right_path)    # 将工作路径改至目标路径

import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ConsoleAdapter  # 避免重复命名
from pathlib import Path

nonebot.init(_env_file=".env")

# 注册适配器
driver = nonebot.get_driver()
driver.register_adapter(ConsoleAdapter)

if __name__ == "__mp_main__":
    nonebot.load_plugins("basic_plugins")
    nonebot.load_plugins("plugins")



if __name__ == "__main__":
    nonebot.load_plugin(
        Path("basic_plugins", "nonebot_plugin_reboot"))
    nonebot.run()