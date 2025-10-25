from fastapi import APIRouter

from model.model import MusicInfo
from service.suggest import suggest_by_one

router = APIRouter(
    prefix="/suggest",
    tags=["suggest"],
)

@router.post("/")
async def gen_suggest_music(music_info: MusicInfo):
    return suggest_by_one(music_info)