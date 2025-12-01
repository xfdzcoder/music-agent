from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse

from core.config import config
from core.db.models.music_info import clear_old_and_save_new, get_by_music_id, find_all
from core.mi.miservice import get_mina_service
from core.mi.player import PlayerHolder
from core.music.music_metadata import load_from_dir


async def aload_local_music():
    music_info_list = await load_from_dir()
    clear_old_and_save_new(music_info_list)


async def download(music_uuid: str):
    file_path = await get_music_file_path(music_uuid)

    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type="application/octet-stream"
    )


async def get_music_file_path(music_uuid: str) -> Path:
    music = get_by_music_id(music_uuid)
    if not music:
        raise HTTPException(status_code=404, detail="music not found")

    file_path = Path(music.filepath)
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="music file not found")
    return file_path


async def play(music_uuid: str):
    music = get_by_music_id(music_uuid)
    if not music:
        raise Exception("music not found!")
    if PlayerHolder.is_play():
        await get_mina_service().player_play(PlayerHolder.device_id())
    else:
        await get_mina_service().play_by_music_url(
            PlayerHolder.device_id(),
            f"{config.get_env('BASE_URL')}/music/download/{music.uuid}",
            1
        )
    PlayerHolder.play(music)


async def pause():
    if PlayerHolder.is_play():
        await get_mina_service().player_pause(PlayerHolder.device_id())
        PlayerHolder.pause()


async def stop():
    await get_mina_service().player_stop(PlayerHolder.device_id())
    PlayerHolder.reset()


async def get_all_music():
    all_music = find_all()
    # TODO 2025/11/30 xfdzcoder: 暂时所有音乐作为播放列表
    PlayerHolder.init_playlist(all_music)
    return all_music
