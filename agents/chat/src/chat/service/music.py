from chat.repository.music import set_json, clear_music, list_music
from core.music.music_metadata import load_from_dir


async def load_local_music():
    music_info_list = await load_from_dir()
    old_music_keys = await list_music()
    for music_info in music_info_list:
        await set_json(music_info)
    await clear_music(old_music_keys)

