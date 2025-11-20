from core.db.models.music_info import clear_old_and_save_new
from core.music.music_metadata import load_from_dir


async def aload_local_music():
    music_info_list = await load_from_dir()
    clear_old_and_save_new(music_info_list)

