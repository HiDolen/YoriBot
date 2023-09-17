import asyncio
from sqlalchemy import create_engine, select, Column, Integer, String
from sqlalchemy.orm import (
    DeclarativeBase,
    sessionmaker,
    mapped_column,
    Mapped,
    Query,
    identity,
)
from sqlalchemy.orm.attributes import instance_dict
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    async_sessionmaker,
    create_async_engine,
)
import os
from pathlib import Path
from datetime import datetime, date
from .path_config import data_path
from utils.static_data_io import StaticDataIO

database_path = data_path / "sign_in_records.sqlite"
json_path = data_path / "sign_in_state.json"


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Sign_In_Record(Base):
    __tablename__ = "sign_in_records"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[str]
    user_id: Mapped[str]
    date: Mapped[date]
    intimate_score_added: Mapped[float]
    reward_points_added: Mapped[int]


class Database:
    def __init__(self) -> None:
        self.engine = create_async_engine(
            "sqlite+aiosqlite:///" + str(database_path), echo=False, future=True
        )
        self.async_session = async_sessionmaker(self.engine, expire_on_commit=True)

    def __await__(self):
        return self.init_database().__await__()

    async def add_record(
        self,
        group_id: str,
        user_id: str,
        date: date,
        intimate_score_added: float = 0,
        reward_points_added: int = 0,
    ):
        async with self.async_session() as session:
            session.add(
                Sign_In_Record(
                    group_id=group_id,
                    user_id=user_id,
                    date=date,
                    intimate_score_added=intimate_score_added,
                    reward_points_added=reward_points_added,
                )
            )
            await session.commit()

    async def record_exists(self, group_id: str, user_id: str, date: date):
        """
        description:
            判断记录是否存在。注意应传入 date 而不是 datetime
        params:
            :param group_id: 群号
            :param user_id: 用户号
            :param date: 日期
        """
        async with self.async_session() as session:
            stmt = select(Sign_In_Record).filter_by(
                group_id=group_id, user_id=user_id, date=date
            )
            if (await session.execute(stmt)).first():
                return True
            return False

    async def get_today_record(self, group_id: str, user_id: str):
        async with self.async_session() as session:
            stmt = select(Sign_In_Record).filter_by(
                group_id=group_id, user_id=user_id, date=datetime.now().date()
            )
            result = (await session.execute(stmt)).first()
            if result:
                return instance_dict(result[0])
            return None

    async def init_database(self):
        if not database_path.exists():
            database_path.parent.mkdir(parents=True, exist_ok=True)
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        return self


class Json(StaticDataIO):
    def __init__(self) -> None:
        super().__init__(json_path)

    def set_sign_in_state(
        self,
        group_id: str,
        user_id: str,
        total_count: int,
        continuous_count: int,
        last_date: date,
    ):
        self.init_group_and_user(group_id, user_id)
        self.data[group_id][user_id] = {
            "total_count": total_count,
            "continuous_count": continuous_count,
            "last_date": last_date.isoformat(),
        }
        self.save()

    def get_sign_in_state(self, group_id: str, user_id: str):
        try:
            return self.data[group_id][user_id]
        except KeyError:
            self.init_group_and_user(group_id, user_id)
            self.save()
            return self.data[group_id][user_id]

    def init_group_and_user(self, group_id: str, user_id: str):
        if group_id not in self.data:
            self.data[group_id] = {}
        if user_id not in self.data[group_id]:
            self.data[group_id][user_id] = {
                "total_count": 0,
                "continuous_count": 0,
                "last_date": date(2020, 1, 1).isoformat(),
            }


# asyncio.run(init_database())
