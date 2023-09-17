import nonebot
import os

path = __file__.rstrip(os.path.basename(__file__))
nonebot.load_plugins(path)