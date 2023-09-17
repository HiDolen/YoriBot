from io import BytesIO
import nonebot
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, Bot
from nonebot.adapters.onebot.v11.permission import GROUP
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot import on_command, on_regex
from nonebot.params import CommandArg, RegexGroup
from pathlib import Path
from .card import get_card
from .data import Database, Json
import asyncio
from datetime import datetime, date
from utils.database_manager import group_member_data
import secrets

backgrounds_path = Path(__file__).parent / "backgrounds"
images_path = Path(__file__).parent / "images"

__plugin_info__ = {
    "plugin_name": "签到",
    "description": "每日签到",
    "usage": "签到",
    "default_status": True,
}


async def init():
    global database, json
    database = await Database()
    json = Json()

asyncio.run(init())


command_start = nonebot.get_driver().config.command_start
sign = on_regex(f'^({"|".join(command_start)})?签到', priority=5, block=True, permission=GROUP)


@sign.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    user_id = event.get_user_id()
    group_id = str(event.group_id)

    state = await update_and_get_data(group_id, user_id)

    image_path = await get_card(bot, user_id, group_id, **state)

    ###
    from utils.image_utils.image_builder import ImageBuilder_Photo
    image = ImageBuilder_Photo(image_path)
    image = image.get_byte_png()
    card = MessageSegment.image(image)
    ###

    # card = MessageSegment.image(image_path)
    await sign.finish(card)


async def update_and_get_data(group_id: str, user_id: str):
    """
    更新签到数据（签到记录、签到数据、好感与金钱），并返回数据用于生成卡片
    """
    date_now = datetime.now().date()
    if not await database.record_exists(group_id, user_id, date_now):
        # 数据库记录
        intimate_score_added = (secrets.randbelow(99)+1)/100
        reward_points_added = secrets.randbelow(100)+1
        await database.add_record(group_id, user_id,
                                  date_now, intimate_score_added, reward_points_added)
        # json 记录
        state = json.get_sign_in_state(group_id, user_id)
        total = state["total_count"] + 1
        last_date = date.fromisoformat(state["last_date"])
        continuous = state["continuous_count"] + 1 if date_now - last_date == 1 else 1
        json.set_sign_in_state(group_id, user_id, total, continuous, date_now)
        # group_member_data 数据更新
        await group_member_data.update_info(
            group_id,
            user_id,
            reward_point_change=reward_points_added,
            intimate_score_change=intimate_score_added,
        )
        info = await group_member_data.get_info(group_id, user_id)
        intimate_score = info["intimate_score"]
        reward_points = info["reward_point"]
    else:
        state = json.get_sign_in_state(group_id, user_id)
        total = state["total_count"]
        continuous = state["continuous_count"]
        info = await group_member_data.get_info(group_id, user_id)
        intimate_score = info["intimate_score"]
        reward_points = info["reward_point"]
        record = await database.get_today_record(group_id, user_id)
        intimate_score_added = record["intimate_score_added"]
        reward_points_added = record["reward_points_added"]

    state = {
        "total_count": total,
        "continuous_count": continuous,
        "intimate_score": intimate_score,
        "reward_points": reward_points,
        "intimate_score_added": intimate_score_added,
        "reward_points_added": reward_points_added,
    }
    return state
