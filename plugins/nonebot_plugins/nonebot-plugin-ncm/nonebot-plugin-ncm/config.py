import nonebot
from pydantic import BaseModel, Extra


# ============Config=============
class Config(BaseModel, extra=Extra.ignore):
    superusers: list = []

    ncm_admin_level: int = 1
    '''设置命令权限(1:仅限superusers和群主,2:在1的基础上管理员,3:所有用户)'''

    ncm_phone: str = ""
    '''手机号'''

    ncm_ctcode: str = "86"
    '''手机号区域码,默认86'''

    ncm_password: str = ""
    '''密码'''

    ncm_playlist_zip: bool = False
    '''上传歌单时是否压缩'''
    ncm_bitrate: int = 320
    '''下载码率(单位K) 96及以下为m4a,320及以上为flac,中间mp3'''


global_config = nonebot.get_driver().config
ncm_config = Config(**global_config.dict())  # 载入配置
