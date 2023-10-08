import nonebot
from datetime import datetime
from nonebot import on_notice, on_request
from nonebot.adapters.onebot.v11 import Bot, GroupIncreaseNoticeEvent, GroupDecreaseNoticeEvent
from utils.global_objects import group_manager
from utils.global_logger import logger
from utils.utils import get_user_name, get_group_name

# bot 被拉入群自动退群、bot 被踢出群进行报告

__force_to_operate__ = True


group_increase_handle = on_notice(priority=1, block=False)
group_decrease_handle = on_notice(priority=1, block=False)


@group_increase_handle.handle()
async def _(bot: Bot, event: GroupIncreaseNoticeEvent):
    if str(event.user_id) == bot.self_id:
        group_id = str(event.group_id)
        operator_id = event.operator_id
        # 允许超级用户任意拉群
        if operator_id in bot.config.superusers:
            return
        if group_manager.group_info.get_group_permission(group_id) <= -1:
            await bot.set_group_leave(group_id=group_id)
            logger.success(f"Bot 主动退出了群 {group_id}")
            return


@group_decrease_handle.handle()
async def _(bot: Bot, event: GroupDecreaseNoticeEvent):
    if event.sub_type == "kick_me":
        group_id = str(event.group_id)
        operator_id = event.operator_id
        operator_name = await get_user_name(bot, operator_id)
        group_name = await get_group_name(bot, group_id)
        for superuser in bot.config.superusers:
            if operator_id == superuser:
                return
            await bot.send_private_msg(
                user_id=superuser,
                message=f"****呜..一份踢出报告****\n"
                f"我被 {operator_name}({operator_id})\n"
                f"踢出了 {group_name}({group_id})\n"
                f"日期：{str(datetime.now()).split('.')[0]}",
            )
