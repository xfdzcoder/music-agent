from typing import Annotated

from fastapi import APIRouter, Path
from starlette.responses import StreamingResponse

from chat.service.music import play, download, stop, pause, get_all_music, get_music_file_path
from core.mi.player import PlayerHolder, PlayMode

router = APIRouter(
    prefix="/music",
    tags=["music"],
)


@router.get("/download/{music_uuid}")
async def download_music(
        music_uuid: Annotated[str, Path(title="music uuid")]
):
    return await download(music_uuid)


@router.get("/inline/{music_uuid}")
async def inline_music(
        music_uuid: Annotated[str, Path(title="music uuid")]
):
    file_path = await get_music_file_path(music_uuid)
    file_like = open(file_path, mode="rb")
    media_type = "audio/flac"

    headers = {
        "Content-Disposition": f'inline; filename="music.flac"',
    }
    return StreamingResponse(file_like, media_type=media_type, headers=headers)


@router.get("/all")
async def list_music():
    return await get_all_music()


@router.post("/play/{music_uuid}")
async def continue_play(
        music_uuid: Annotated[str, Path(title="music uuid")],
):
    await play(music_uuid)


@router.put("/pause")
async def pause_music():
    await pause()


@router.put("/mode/{mode}")
async def update_mode(
        mode: Annotated[PlayMode, Path(title="mode")]
):
    PlayerHolder.get().mode = mode


@router.put("/volume/{volume}")
async def update_volume(
        volume: Annotated[int, Path(title="volume")]
):
    PlayerHolder.get().volume = volume


@router.get("/state")
async def state():
    return PlayerHolder.get().dumps()


@router.delete("/stop/{music_uuid}")
async def stop_music(
        music_uuid: Annotated[str, Path(title="music uuid")]  # noqa
):
    await stop()
