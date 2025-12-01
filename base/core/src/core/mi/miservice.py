import json
from typing import Literal

from aiohttp import ClientSession
from pydantic import BaseModel

from core.config import config
from core.logger.logger import logger
from miservice import MiAccount, MiNAService

MiDeviceHardware = Literal[
    "OH2P"
]


class MiDevice(BaseModel):
    name: str
    device_id: str
    did: str
    presence: str
    hardware: MiDeviceHardware


_mi_account: MiAccount | None = None
_mina_service: MiNAService | None = None
_devices: list[MiDevice] = []


async def init_mi(session: ClientSession):
    global _mi_account, _mina_service, _devices
    _mi_account = MiAccount(
        session,
        config.get_env("MI_USERNAME"),
        config.get_env("MI_PASSWORD")
    )
    _mina_service = MiNAService(_mi_account)
    devices = await _mina_service.device_list()
    for device in devices:
        mi_device = MiDevice(
            name=device["name"],
            device_id=device["deviceID"],
            did=device["miotDID"],
            presence=device["presence"],
            hardware=device["hardware"]
        )
        logger.info("find device " + mi_device.name)
        _devices.append(mi_device)


def get_mi_account() -> MiAccount:
    global _mi_account
    return _mi_account


def get_mina_service() -> MiNAService:
    global _mina_service
    return _mina_service


def get_devices() -> list[MiDevice]:
    global _devices
    return _devices


def get_device(device_id: str) -> MiDevice | None:
    global _devices
    for device in _devices:
        if device.device_id == device_id:
            return device
    return None

async def is_playing(device_id: str) -> bool:
    global _mina_service
    player_status_response = await _mina_service.player_get_status(device_id)
    return json.loads(player_status_response["data"]["info"])["status"] == "1"