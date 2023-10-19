from nonebot.matcher import matchers, Matcher
from nonebot import Bot
from typing import List

async def get_group_name(bot:Bot, group_id:str) -> str:
    try:
        info = await bot.get_group_info(group_id=group_id)
        return info['group_name']
    except:
        return None

async def get_user_name(bot:Bot, user_id:str) -> str:
    try:
        info = await bot.get_stranger_info(user_id=user_id)
        return info['nickname']
    except:
        return None

async def get_group_member_name(bot:Bot, group_id:str, user_id:str) -> str:
    try:
        info = await bot.get_group_member_info(group_id=group_id, user_id=user_id)
        return info['nickname']
    except:
        return None

def get_matchers(distinct: bool = False) -> List[Matcher]:
    """
    description:
        获取所有 matcher
    params:
        :param distinct: 是否去重
    """
    matchers_list = []
    temp_names = []
    for i in matchers.keys():
        for matcher in matchers[i]:
            if distinct and matcher.plugin_name in temp_names:
                continue
            matchers_list.append(matcher)
            temp_names.append(matcher.plugin_name)
    return matchers_list

def trim_docstring(docstring: str) -> str:
    """
    description:
        去除 docstring 开头与结尾的空行、空格
    params:
        :param docstring: docstring
    """
    docstring = docstring.strip()
    while docstring.startswith("\n"):
        docstring = docstring[1:]
    while docstring.endswith("\n"):
        docstring = docstring[:-1]
    return docstring
