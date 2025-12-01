from sqlalchemy import String, BigInteger, Integer, Text, select, text, delete, Result
from sqlalchemy.dialects.postgresql import TSVECTOR, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, Session

from core.db import postgres
from core.db.models import Base

from core.db.models.base import BaseDto
from core.utils.snowflake_utils import gen_snowflake_id


class MusicInfoModel(Base):
    __tablename__ = "music_info"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, default=lambda: gen_snowflake_id())
    uuid: Mapped[str] = mapped_column(String(64))
    filepath: Mapped[str | None] = mapped_column(String(255))
    album: Mapped[str | None] = mapped_column(String(255))
    title: Mapped[str | None] = mapped_column(String(255))
    artist: Mapped[list[str] | None] = mapped_column(ARRAY(Text, zero_indexes=True))
    date: Mapped[int | None] = mapped_column(Integer)
    lyrics: Mapped[str | None] = mapped_column(Text)
    album_artist: Mapped[str | None] = mapped_column(String(255))
    time_length: Mapped[int | None] = mapped_column(Integer)
    search_vector: Mapped[str] = mapped_column(TSVECTOR)
    pictures: Mapped[list[str] | None] = mapped_column(ARRAY(Text, zero_indexes=True))


class MusicInfo(BaseDto):
    uuid: str
    filepath: str
    album: str
    title: str
    artist: list[str]
    date: int
    lyrics: str
    album_artist: str
    time_length: int
    pictures: list[str]

    @classmethod
    def to_music_info_list(cls, result: Result[MusicInfoModel]) -> list["MusicInfo"]:
        return [MusicInfo.model_validate(item) for item in result.scalars().all()]


def search_music(keyword: str) -> list[MusicInfo]:
    with postgres.get_session() as session:
        # 使用 websearch_to_tsquery，更接近自然语言搜索
        stmt = select(MusicInfoModel).where(
            MusicInfoModel.search_vector.op("@@")(text("websearch_to_tsquery(:kw)"))
        ).params(kw=keyword)

        result = session.execute(stmt)
        return MusicInfo.to_music_info_list(result)


def clear_old_and_save_new(music_infos: list[MusicInfo]):
    with postgres.get_session() as session:
        stmt = delete(MusicInfoModel)
        session.execute(stmt)
        _do_save_batch(music_infos, session)


def _do_save_batch(music_infos: list[MusicInfo], session: Session):
    data_list = [
        MusicInfoModel(
            uuid=info.uuid,
            filepath=info.filepath,
            album=info.album,
            title=info.title,
            artist=info.artist,
            date=info.date,
            lyrics=info.lyrics,
            album_artist=info.album_artist,
            time_length=info.time_length,
            pictures=info.pictures,
        )
        for info in music_infos
    ]
    session.add_all(data_list)


def get_by_music_id(music_uuid: str) -> MusicInfo | None:
    with postgres.get_session() as session:
        stmt = select(MusicInfoModel).where(MusicInfoModel.uuid == music_uuid)
        music_info_model = session.execute(stmt).scalar_one_or_none()
        return MusicInfo.model_validate(music_info_model)


def find_all():
    with postgres.get_session() as session:
        stmt = select(MusicInfoModel)
        result = session.execute(stmt)
        return MusicInfo.to_music_info_list(result)