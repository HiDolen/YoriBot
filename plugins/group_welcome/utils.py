import anyio
import re
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from nonebot.internal.adapter.template import MessageTemplate
import httpx
from pathlib import Path
from utils.utils import get_group_member_name
from .path_config import image_dir

from .data import welcomeMsg, images

# 创建 image_dir 路径
image_dir.mkdir(parents=True, exist_ok=True)


async def save_image(msg: Message):
    async def download_image(url: str):
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            return resp.content

    async def save_to_file(name: str, img: bytes):
        all_name = images.get_all_name()
        path = image_dir / name
        if name not in all_name:
            async with await anyio.open_file(path, "wb") as f:
                await f.write(img)
        images.add_a_image(name)  # 记录图片，或者 use_count + 1

    for m in msg:
        if m.type == "image":
            filename = m.data["file"]
            # 替换后缀为 .jpg
            filename = re.sub(r"\.\w+$", ".jpg", filename)
            url = m.data["url"]
            img = await download_image(url)
            await save_to_file(filename, img)


def delete_image(msg: str):
    msg = Message(msg)
    for m in msg:
        if m.type == "image":
            filename = m.data["file"]
            filename = re.sub(r"^file:///", "", filename)
            filename = Path(filename).with_suffix(".jpg").name
            if images.delete_a_image(filename):
                (image_dir / filename).unlink()


def message2string(msg: Message):
    value = ""
    for m in msg:
        if m.type == "text":
            value += m.data["text"]
        elif m.type == "at":
            value += f"[CQ:at,qq={m.data['qq']}]"
        elif m.type == "face":
            value += f"[CQ:face,id={m.data['id']}]"
        elif m.type == "image":
            filename = m.data["file"]
            filename = re.sub(r"\.\w+$", ".jpg", filename)
            value += f"[CQ:image,file=file:///{(image_dir / filename).resolve()}]"
        else:
            raise ValueError(f"不支持的消息类型：{m.type}")
    return value.strip()


def string2message(value: str, user_id: str = None):
    """
    将 value 转换成 Message 类型
    """  # TODO 未测试 at 部分
    if user_id:
        value = re.sub(r"\[at\]", lambda x: f"[CQ:at,qq={user_id}]", value)
    message = Message(value)
    return message


def truncate_str(string: str, length: int):
    """
    截断字符串，超过长度的部分用 ... 代替
    """
    if len(string) <= length:
        return string
    return string[:length] + "..."


def match_from_message(msg: Message, group_id: str):
    """
    从消息中匹配词条
    """
    msg = message2string(msg)
    all_key = welcomeMsg.get_all_key(group_id)
    values = []
    for key in all_key:
        for v in welcomeMsg.get_all_value_from_a_key(group_id, key):
            if v["match_type"] == 1:
                if msg == key:
                    values.append(v["value"])
            elif v["match_type"] == 2:
                if key in msg:
                    values.append(v["value"])
    return values
