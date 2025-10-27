from pydantic import BaseModel, RootModel, Field


class MusicInfo(BaseModel):
    name: str = Field(description="歌名")
    author: str = Field(description="歌手")

class MusicInfoList(RootModel[list[MusicInfo]]):
    root: list[MusicInfo] = Field(description="音乐信息列表")