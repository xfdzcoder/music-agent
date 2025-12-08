import asyncio
import json
from typing import Literal

from core.config import config
from core.context.context import ContextHolder
from core.db.models.music_info import MusicInfo
from core.logger.logger import logger
from core.mi.miservice import MiDevice, get_mina_service, get_devices
from core.utils import list_utils
from core.utils.time_utils import MusicTimer

PlayMode = Literal["order", "single", "loop", "random"]
LOOP_TYPE : dict[PlayMode, int] = {
    "order": 2,
    "single": 0,
    "loop": 1,
    "random": 3,
}
StatusType = Literal["playing", "pause", "none"]
STATUS_TYPE : dict[int, StatusType] = {
    1: "playing",
    2: "pause",
    3: "none",
}
LIGHT_TYPE : dict[int, bool] = {
    1: True,
    2: False,
}



class Player:

    def __init__(self):
        self.play_status = "none"
        self.mode: PlayMode = "loop"
        self.device: MiDevice | None = list_utils.get_first(get_devices())
        self.playlist: list[MusicInfo] = []
        self.music: MusicInfo | None = None
        self.index: int | None = None
        self.volume = -1
        self.timer = MusicTimer()

        self._loop_device_status()

    def _loop_device_status(self):
        async def _loop():
            while True:
                if not self.device:
                    return
                player_status_response = await get_mina_service().player_get_status(self.device.device_id)
                logger.info(f"player_status_response: \n{player_status_response}")
                info = json.loads(player_status_response["data"]["info"])
                self.play_status = STATUS_TYPE.get(info["status"])
                self.volume = info["volume"]
                if info["loop_type"] == 1:
                    self.mode = "loop"
                await asyncio.sleep(5)

        asyncio.create_task(_loop())

    async def _play_next(self):
        self.timer.stop()
        if self.mode == "loop":
            next_index = (self.index + 1) % len(self.playlist)
            await self.play(self.playlist[next_index])
        elif self.mode == "order":
            next_index = self.index + 1
            if next_index < len(self.playlist):
                await self.play(self.playlist[next_index])
        else:
            await self.play(self.playlist[self.index])

    async def play(self, music: MusicInfo):
        is_current_music = self.music and self.music.uuid == music.uuid
        if is_current_music and await PlayerHolder.is_pause():
            await get_mina_service().player_play(PlayerHolder.device_id())
        else:
            await get_mina_service().play_by_music_url(
                PlayerHolder.device_id(),
                f"{config.get_env('BASE_URL')}/music/download/{music.uuid}",
                LIGHT_TYPE[1]
            )

        if self.music and self.music.uuid != music.uuid:
            self.timer.stop()
        self.index = list_utils.index(self.playlist, music.uuid, lambda m: m.uuid)
        self.music = music
        self.timer.load(ContextHolder.get(), music.time_length * 1000, self._play_next)
        self.timer.play()

    async def pause(self):
        if self.play_status != "playing":
            return
        await get_mina_service().player_pause(PlayerHolder.device_id())
        self.timer.pause()

    async def dumps(self):
        return {
            "mode": self.mode,
            "is_playing": self.play_status == "playing",
            "volume": self.volume,
            "music": self.music if self.music else None,
            "device": self.device if self.device else None,
            "playlist": self.playlist,
            "position_ms": self.timer.get_position_ms(),
            "index": self.index,
        }


class PlayerHolder:
    players: dict[str, Player] = {}

    @classmethod
    def get(cls) -> Player:
        return cls.players.get(ContextHolder.user_id())

    @classmethod
    async def init(cls):
        if not cls.players.get(ContextHolder.user_id()):
            cls.players[ContextHolder.user_id()] = Player()

    @classmethod
    async def reset(cls):
        await get_mina_service().player_stop(PlayerHolder.device_id())
        cls.players[ContextHolder.user_id()] = Player()

    @classmethod
    async def init_playlist(cls, musics: list[MusicInfo]):
        if not musics:
            return
        cls.get().playlist = musics

    @classmethod
    async def is_play(cls):
        return cls.get().play_status == "playing"

    @classmethod
    async def is_pause(cls):
        return cls.get().play_status == "pause"

    @classmethod
    def device_id(cls):
        return cls.get().device.device_id

    @classmethod
    async def play(cls, music: MusicInfo):
        await cls.get().play(music)

    @classmethod
    async def pause(cls):
        await cls.get().pause()

    @classmethod
    async def set_loop_type(cls, loop_type: PlayMode):
        cls.get().mode = loop_type
