from pydantic import BaseModel


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


