from io import BytesIO
import nonebot
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, Bot
from nonebot.adapters.onebot.v11.permission import GROUP
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot import on_command, on_regex
from nonebot.params import CommandArg, RegexGroup
from pathlib import Path
from datetime import date, datetime
from configs.path_config import DATA_PATH
import httpx
from utils.image_utils.image_builder import ImageBuilder, ImageBuilder_Text, ImageBuilder_Photo
from utils.utils import get_group_member_name
from PIL import Image
import os
import random
from configs.path_config import TEMP_PATH
from .path_config import backgrounds_path, images_path

async def get_card(
        bot: Bot, 
        user_id, 
        group_id,
        *,
        total_count: int = 1,
        continuous_count: int = 1,
        intimate_score: float = 0,
        reward_points: int = 0,
        intimate_score_added: float = 0,
        reward_points_added: int = 0,):
    image_path = Path(TEMP_PATH, f'{datetime.now().date()}_sign_in_{group_id}_{user_id}.png')
    image_path = image_path.absolute()
    if image_path.exists():
        return image_path
    
    nickname = await get_group_member_name(bot, group_id, user_id)
    if not nickname:
        nickname = '我名字呢？'

    card = await generate_card(
        user_id,
        nickname,
        total_count,
        continuous_count,
        intimate_score,
        reward_points,
        intimate_score_added,
        reward_points_added,
    )
    card.save(image_path)
    return image_path



async def generate_card(
    user_id: str,
    nickname: str,
    total_count: int,
    continuous_count: int,
    intimate_score: float,
    reward_points: int,
    intimate_score_added: float,
    reward_points_added: int,
):
    profile_image = await get_profile_image(user_id, 102)
    if not profile_image:
        return None
    profile_image = ImageBuilder_Photo(BytesIO(profile_image))
    # profile_image = ImageBuilder_Photo('./QQ截图20230614224852.png')
    profile_image.resize(w=102)
    #####

    profile_image_back = ImageBuilder_Photo(images_path / 'profile_image_border.png')
    profile_image_back.resize(w=140)
    profile_image.cut_to_circle()
    profile_image_back.paste_image(profile_image, align=("center", "center"))
    profile_image = profile_image_back


    background_image = random.choice(os.listdir(backgrounds_path))
    background_image = ImageBuilder_Photo(backgrounds_path / background_image)
    background_image.cut_and_resize(876, 424)

    transparent_image = ImageBuilder(876, 274)
    transparent_image = Image.new("RGBA", (876, 274), (255, 255, 255, 120))
    transparent_image = ImageBuilder_Photo(transparent_image)

    # 昵称文字
    nickname_image = ImageBuilder_Text(nickname, 50, (255, 255, 255, 255), "yz.ttf")

    # 累计签到文字
    total_count_image = ImageBuilder_Text(
        f"累计签到", 35, (0, 0, 0, 255), "yz.ttf")
    total_count_image.join_image(
        ImageBuilder_Text(f"{total_count}", 45, (210, 71, 41, 255), "yz.ttf"),
        spacing=10, align="bottom"
    )
    total_count_image.join_image(
        ImageBuilder_Text("days", 35, (0, 0, 0, 255), "yz.ttf"),
        spacing=10, align="bottom"
    )

    # 好感度文字
    intimate_score_image = ImageBuilder_Text("当前", 20, (0, 0, 0, 255), "yz.ttf")
    intimate_score_image.join_image(
        ImageBuilder_Text(f"好感度：{intimate_score:.2f}", 30, (0, 0, 0, 255), "yz.ttf"),
        spacing=5)
    intimate_score_image.join_image(
        ImageBuilder_Text(f"+{intimate_score_added:.2f}", 18, (210, 71, 41, 255), "yz.ttf"),
        align="bottom", spacing=5)
    
    # 三句话，合并到好感度文字
    text1 = f"金币 + {reward_points_added}"
    text2 = f"连续签到 {continuous_count} 天"
    text3 = ""
    texts = [text1, text2, text3]
    for text in texts:
        intimate_score_image.join_image_vertical(
            ImageBuilder_Text(text, 20, (66, 66, 66, 255), "yz.ttf"),
            align="left", spacing=5)
        
    # 时间文字
    time_image = ImageBuilder_Text(
        f'时间：{datetime.now().strftime("%Y-%m-%d %a %H:%M:%S")}',
        20, (0, 0, 0, 255), "yz.ttf")
    # intimate_score_image.join_image_vertical(time_image, align="left", spacing=5)
    
    

    # 复制到透明图
    transparent_image.paste_image(profile_image, offset=(90, 0), align=("left", "center"))
    transparent_image.paste_image(total_count_image, offset=(250, 16))
    transparent_image.paste_image(intimate_score_image, offset=(300, 90))
    transparent_image.paste_image(time_image, offset=(500, 200))
    # 复制到背景图
    background_image.paste_image(nickname_image, offset=(50, 50))
    background_image.paste_image(transparent_image, align=("center", "bottom"))

    return background_image


async def get_profile_image(
        user_id: str,
        size: int = 160,
):
    url1 = f'http://q1.qlogo.cn/g?b=qq&nk={user_id}&s={size}'
    url2 = f'http://q2.qlogo.cn/headimg_dl?dst_uin={user_id}&spec={size}'
    # 根据 url 拉取图片
    async with httpx.AsyncClient() as client:
        for _ in range(3):
            try:
                if content :=  (await client.get(url1)).content:
                    return content
                else:
                    continue
            except:
                pass
        for _ in range(3):
            try:
                if content :=  (await client.get(url2)).content:
                    return content
                else:
                    continue
            except:
                pass
    return None