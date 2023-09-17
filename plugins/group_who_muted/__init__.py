from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11 import GroupBanNoticeEvent
from nonebot import on_command, on_regex, on_message, on_notice
from nonebot.plugin import PluginMetadata
from utils.utils import get_group_member_name, get_user_name
import json
import os
from datetime import datetime, timedelta
import random
import re

__plugin_meta__ = PluginMetadata(
    name="小黑屋提醒",
    description=r"有人被关小黑屋时提醒",
    type="application",
    supported_adapters={"~onebot.v11"},
    usage="None",
)

sentences = []
with open(
    os.path.join(os.path.dirname(__file__), "sentences.json"), "r", encoding="utf-8"
) as f:
    sentences = json.load(f)

records = {}


muted = on_notice(priority=1, block=False)


@muted.handle()
async def mutedSatire(bot: Bot, event: GroupBanNoticeEvent):
    group_id = str(event.group_id)
    user_id = str(event.user_id)

    if group_id not in records:
        records[group_id] = {}
    time_before = records[group_id].get(user_id, None)
    time_before = (
        datetime.strptime(time_before, "%Y-%m-%d %H:%M:%S")
        if time_before
        else datetime.now()
    )
    time_now = datetime.now()
    time_delta = time_now - time_before
    if time_delta > timedelta(hours=1):
        sentence = random.choice(sentences["first"])
    else:
        sentence = random.choice(sentences["second"])
    records[group_id][user_id] = time_now.strftime("%Y-%m-%d %H:%M:%S")

    seconds = event.duration
    if seconds == 0:
        return
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    time = ""
    if d != 0:
        time += f"{d}天"
    if h != 0:
        time += f"{h}小时"
    if m != 0:
        time += f"{m}分钟"
    if s != 0:
        time += f"{s}秒"

    user_name = (
        await get_group_member_name(bot, group_id, user_id)
        or await get_user_name(bot, user_id)
        or user_id
    )
    sex = (
        await bot.get_group_member_info(group_id=event.user_id, user_id=event.group_id)
    )["sex"]
    sex = "他" if sex == "male" else "她" if sex == "female" else "这位群友"

    sentence = re.sub(r"\{user_name\}", user_name, sentence)
    sentence = re.sub(r"\{sex\}", sex, sentence)
    sentence = re.sub(r"\{time\}", time, sentence)

    await muted.send(sentence)
