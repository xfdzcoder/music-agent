from pydantic import BaseModel, ConfigDict


class MusicInfo(BaseModel):
    uuid: str
    filepath: str
    album: str
    title: str
    artist: list[str]
    date: int
    lyrics: str
    album_artist: str
    time_length: int

    model_config = ConfigDict(from_attributes=True)


