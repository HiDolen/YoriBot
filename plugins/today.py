import random
from datetime import date
from nonebot.plugin import on_keyword, on_regex
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.adapters.onebot.v11.message import Message
from nonebot.plugin import PluginMetadata
import nonebot

__plugin_meta__ = PluginMetadata(
    name="今日人品",
    description=r"今天的运势",
    usage="今日人品, jrrp",
    type="application",
    extra={
        "default_status": False
    }
)


def luck_simple(num):
    if num < 18:
        return '大吉'
    elif num < 53:
        return '吉'
    elif num < 58:
        return '半吉'
    elif num < 62:
        return '小吉'
    elif num < 65:
        return '末小吉'
    elif num < 71:
        return '末吉'
    else:
        return '凶'

command_start = nonebot.get_driver().config.command_start
command_start = '|'.join(command_start)

# jrrp = on_keyword(['jrrp','今日人品'],priority=50)
# command_start 可有可无
jrrp = on_regex(f'^{command_start}?(jrrp|今日人品)$', priority=50)

@jrrp.handle()
async def jrrp_handle(bot: Bot, event: Event):
    rnd = random.Random()
    rnd.seed(int(date.today().strftime("%y%m%d")) + int(event.get_user_id()))
    lucknum = rnd.randint(1,100)
    await jrrp.finish(Message(f'[CQ:at,qq={event.get_user_id()}]您今日的幸运指数是{lucknum}/100（越低越好），为"{luck_simple(lucknum)}"'))
