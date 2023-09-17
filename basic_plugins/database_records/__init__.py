# from .database import Database, Group_Change, Group_Rename

# from nonebot import on_notice
# from nonebot.adapters.onebot.v11 import Bot, GroupIncreaseNoticeEvent, GroupDecreaseNoticeEvent

# group_member_increase = on_notice(priority=1, block=False)
# group_member_decrease = on_notice(priority=1, block=False)

# database = Database("records", "records")

# @group_member_increase.handle()
# async def _(bot: Bot, event: GroupIncreaseNoticeEvent):
#     info = Group_Change(
#         time=event.time,
#         type="increase",
#         group_id=event.group_id,
#         operator_id=event.operator_id,
#         user_id=event.user_id
#     )
#     database.session.add(info)
#     database.session.commit()

# @group_member_decrease.handle()
# async def _(bot: Bot, event: GroupDecreaseNoticeEvent):
#     info = Group_Change(
#         time=event.time,
#         type="decrease",
#         group_id=event.group_id,
#         operator_id=event.operator_id,
#         user_id=event.user_id
#     )
#     database.session.add(info)
#     database.session.commit()