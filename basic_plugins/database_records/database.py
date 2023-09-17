# 使用 sqlalchemy 存储数据
# 在人员变动、改名
# 群人员变动，包括 成员加减

import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from utils.global_objects import global_database_base as Base
from configs.path_config import DB_PATH

class Database:
    def __init__(self, name: str, new_folder: str = None):
        group_change_record = Group_Change()
        group_rename_record = Group_Rename()

        if new_folder:
            self.database_path = f"sqlite:///{DB_PATH}/{new_folder}/{name}.sqlite"
        else:
            self.database_path = f"sqlite:///{DB_PATH}/{name}.sqlite"

        
        self.engine = create_engine(self.database_path, echo=False)
        session = Base.sessionmaker(bind=self.engine)()


class Group_Change(Base):
    __tablename__ = "member_change_record"

    time = Column(DateTime, nullable=False)
    type = Column(String, nullable=False) # 用于区别不同动作
    group_id = Column(String, nullable=False)
    operator_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)

    TYPE = (
        'increase',
        'decrease',
    )

class Group_Rename(Base):
    __tablename__ = "group_rename_record"

    time = Column(DateTime, nullable=False)
    group_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    card_new = Column(String, nullable=True)
    card_old = Column(String, nullable=True)