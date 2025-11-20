from datetime import datetime

from sqlalchemy import BigInteger, DateTime
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

from core.utils.snowflake_utils import gen_snowflake_id


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, default=lambda: gen_snowflake_id())

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )
