from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse

from core.db.models.music_info import clear_old_and_save_new, get_by_music_id, find_all
from core.mi.miservice import get_mina_service
from core.mi.player import PlayerHolder, PlayMode
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
    await PlayerHolder.play(music)


async def pause():
    await PlayerHolder.pause()


async def stop():
    await PlayerHolder.reset()


async def set_volume(volume: int):
    await get_mina_service().player_set_volume(PlayerHolder.device_id(), volume)

async def set_loop_type(loop_type: PlayMode):
    await PlayerHolder.set_loop_type(loop_type)


async def get_all_music():
    all_music = find_all()
    # TODO 2025/11/30 xfdzcoder: 暂时所有音乐作为播放列表
    await PlayerHolder.init_playlist(all_music)
    return all_music
