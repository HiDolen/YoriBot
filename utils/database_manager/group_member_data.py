import asyncio
from sqlalchemy import create_engine, select, Column, Integer, String
from sqlalchemy.orm import (
    DeclarativeBase,
    sessionmaker,
    mapped_column,
    Mapped,
    Query,
)
from sqlalchemy.orm.attributes import instance_dict
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    async_sessionmaker,
    create_async_engine,
)
from configs.path_config import DATA_PATH

database_path = DATA_PATH / "group_member_data.sqlite"


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Reward_and_Intimate(Base):
    __tablename__ = "reward_and_intimate"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[str]
    user_id: Mapped[str]
    reward_point: Mapped[int]
    intimate_score: Mapped[float]


engine = create_async_engine(
    "sqlite+aiosqlite:///" + str(database_path), echo=False, future=True
)

async_session = async_sessionmaker(engine, expire_on_commit=True)


async def update_info(
    group_id: str,
    user_id: str,
    reward_point_change: int = 0,
    intimate_score_change: float = 0,
):
    """
    如果数据库中没有相同 group_id、user_id 的信息，则创建，否则更新
    """
    async with async_session() as session:
        async with session.begin():
            select_stmt = select(Reward_and_Intimate).filter_by(
                group_id=group_id, user_id=user_id
            )
            result = await session.execute(select_stmt)
            result = result.fetchone()
            if result is None:
                session.add(
                    Reward_and_Intimate(
                        group_id=group_id,
                        user_id=user_id,
                        reward_point=reward_point_change,
                        intimate_score=intimate_score_change,
                    )
                )
            else:
                result[0].reward_point += reward_point_change
                result[0].intimate_score += intimate_score_change
        await session.commit()


async def get_info(group_id: str, user_id: str):
    async with async_session() as session:
        select_stmt = select(Reward_and_Intimate).filter_by(
            group_id=group_id, user_id=user_id
        )
        result = await session.execute(select_stmt)
        result = result.fetchone()
        if result is None:
            await update_info(group_id, user_id)
            return await get_info(group_id, user_id)
        else:
            return instance_dict(result[0])


async def init_database():
    if not database_path.exists():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


asyncio.run(init_database())
