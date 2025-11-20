from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import select

from core.context.context import ContextHolder
from core.db import postgres
from core.db.models import Base
from core.db.models.base import BaseDto


class UserThreadModel(Base):
    __tablename__ = "user_thread"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    thread_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))


class UserThread(BaseDto):
    user_id: str
    thread_id: str
    name: str
    created_at: datetime
    updated_at: datetime


def list_thread() -> list[UserThread]:
    with postgres.get_session() as session:
        stmt = (
            select(UserThreadModel)
                .where(UserThreadModel.user_id == ContextHolder.user_id())
                .order_by(UserThreadModel.created_at.desc())
        )
        result = session.execute(stmt)
        return [UserThread.model_validate(user_thread) for user_thread in result.scalars().all()]


def add_or_update_thread(thread_id: str, name: str = "Chat"):
    with postgres.get_session() as session:
        stmt = select(UserThreadModel).where(
            UserThreadModel.user_id == ContextHolder.user_id(),
            UserThreadModel.thread_id == thread_id
        )
        existed = session.execute(stmt).scalar_one_or_none()

        if existed:
            existed.updated_at = datetime.now()
            existed.name = name
        else:
            thread = UserThreadModel(
                user_id=ContextHolder.user_id(),
                thread_id=thread_id,
                name=name,
            )
            session.add(thread)

        session.commit()


def get_name_by_thread_id() -> str:
    with postgres.get_session() as session:
        stmt = select(UserThreadModel).where(
            UserThreadModel.user_id == ContextHolder.user_id(),
            UserThreadModel.thread_id == ContextHolder.thread_id()
        )
        user_thread : UserThreadModel = session.execute(stmt).scalar_one_or_none()
        if user_thread:
            return user_thread.name
        return "Chat"
