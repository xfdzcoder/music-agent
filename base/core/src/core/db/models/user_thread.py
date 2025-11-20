from datetime import datetime
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import select

from core.context.context import ContextHolder
from core.db import postgres
from core.db.models import Base


class UserThreadModel(Base):
    __tablename__ = "user_thread"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    thread_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))


def list_thread() -> list[UserThreadModel]:
    with postgres.get_session() as session:
        stmt = select(UserThreadModel).where(UserThreadModel.user_id == ContextHolder.user_id())
        result = session.execute(stmt)
        return list(result.scalars().all())


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
