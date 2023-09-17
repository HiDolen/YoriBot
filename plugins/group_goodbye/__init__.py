from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11 import GroupDecreaseNoticeEvent
from nonebot import on_command, on_regex, on_message, on_notice
from nonebot.plugin import PluginMetadata
from utils.utils import get_group_member_name, get_user_name

__plugin_meta__ = PluginMetadata(
    name="退群提醒",
    description=r"有人退群时提醒",
    type="application",
    supported_adapters={"~onebot.v11"},
    usage="None",
)


goodbye = on_notice(priority=1, block=False)


@goodbye.handle()
async def _(bot: Bot, event: GroupDecreaseNoticeEvent):
    if not event.sub_type == "leave":
        return
    group_id = str(event.group_id)
    user_id = str(event.user_id)
    user_name = (
        await get_group_member_name(bot, group_id, user_id)
        or await get_user_name(bot, user_id)
        or None
    )
    if user_name:
        goodbye.finish(f"{user_name}（{user_id}）离开了我们...")
    else:
        goodbye.finish(f"{user_id} 离开了我们...")
