import asyncio
import json
from typing import Literal

from core.context.context import ContextHolder
from core.db.models.music_info import MusicInfo
from core.mi.miservice import MiDevice, get_mina_service, get_devices
from core.utils import list_utils
from core.utils.time_utils import MusicTimer

PlayMode = Literal["order", 'single', 'loop']


class Player:

    def __init__(self):
        self.mode: PlayMode = "loop"
        self.device: MiDevice | None = list_utils.get_first(get_devices())
        self.playlist: list[MusicInfo] = []
        self.music: MusicInfo | None = None
        self.index: int | None = None
        self.is_playing = False
        self.volume = -1
        self.timer = MusicTimer()

        self._loop_device_status()

    def _loop_device_status(self):
        async def _loop():
            while True:
                if not self.device:
                    return
                player_status_response = await get_mina_service().player_get_status(self.device.device_id)
                info = json.loads(player_status_response["data"]["info"])
                self.is_playing = info["status"] == 1
                self.volume = info["volume"]
                if info["loop_type"] == 1:
                    self.mode = "loop"
                await asyncio.sleep(5)

        asyncio.create_task(_loop())

    def _play_next(self):
        self.timer.stop()
        if self.mode == "loop":
            next_index = (self.index + 1) % len(self.playlist)
            self.play(self.playlist[next_index])
        elif self.mode == "order":
            next_index = self.index + 1
            if next_index < len(self.playlist):
                self.play(self.playlist[next_index])
        else:
            self.play(self.playlist[self.index])

    def play(self, music: MusicInfo):
        if self.music and self.music.uuid != music.uuid:
            self.timer.stop()
        self.index = list_utils.index(self.playlist, music.uuid, lambda m: m.uuid)
        self.music = music
        self.is_playing = True
        self.timer.load(music.time_length * 1000, self._play_next)
        self.timer.play()

    def pause(self):
        if not self.is_playing:
            return
        self.is_playing = False
        self.timer.pause()

    def dumps(self):
        return {
            "mode": self.mode,
            "is_playing": self.is_playing,
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
    def init(cls):
        if not cls.players.get(ContextHolder.user_id()):
            cls.players[ContextHolder.user_id()] = Player()

    @classmethod
    def reset(cls):
        cls.players[ContextHolder.user_id()] = Player()

    @classmethod
    def init_playlist(cls, musics: list[MusicInfo]):
        if not musics:
            return
        cls.get().playlist = musics

    @classmethod
    def is_play(cls, music: MusicInfo | None = None):
        if music:
            return cls.get().is_playing and cls.get().music and cls.get().music.uuid == music.uuid
        return cls.get().is_playing

    @classmethod
    def device_id(cls):
        return cls.get().device.device_id

    @classmethod
    def play(cls, music: MusicInfo):
        cls.get().play(music)

    @classmethod
    def pause(cls):
        cls.get().pause()
