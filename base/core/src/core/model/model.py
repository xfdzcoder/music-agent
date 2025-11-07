from pydantic import BaseModel, RootModel, Field


class MusicInfo(BaseModel):
    name: str = Field(description="歌名")
    author: str = Field(description="歌手")

class MusicInfoList(RootModel[list[MusicInfo]]):
    root: list[MusicInfo] = Field(description="音乐信息列表", default_factory=list)

    @classmethod
    def add_music_info_list(cls, old: "MusicInfoList", new: "MusicInfoList"):
        old_root = old.root if old else []
        new_root = new.root if new else []

        return cls(root=old_root + new_root)