import asyncio
import os
from time import sleep

from aiohttp import ClientSession
from dotenv import load_dotenv, find_dotenv

from miservice import MiAccount, MiNAService


async def main():
    username = os.getenv("MI_USERNAME")
    password = os.getenv("MI_PASSWORD")

    async with ClientSession() as session:
        mi_account = MiAccount(session, username, password)
        mina_service = MiNAService(mi_account)
        devices = await mina_service.device_list()
        device = devices[0]
        device_id = device["deviceID"]
        await mina_service.play_by_music_url(
            device_id,
            "https://xiaomusic.xfdzcoder.space:443/music/G.E.M.%E9%82%93%E7%B4%AB%E6%A3%8B/%E6%96%B0%E7%9A%84%E5%BF%83%E8%B7%B3/G.E.M.%E9%82%93%E7%B4%AB%E6%A3%8B-%E5%A4%9A%E8%BF%9C%E9%83%BD%E8%A6%81%E5%9C%A8%E4%B8%80%E8%B5%B7.flac"
        )
        # print("player_play:\n", await mina_service.player_play(device_id))
        print("player_get_status:\n", await mina_service.player_get_status(device_id))
        sleep(10)
        print("player_pause:\n", await mina_service.player_pause(device_id))
        # print(
        #     "player_pause:\n",
        #     await mina_service.ubus_request(
        #         device_id,
        #         "player_play_operation",
        #         "mediaplayer",
        #         {"action": "pause", "media": "app_ios"},
        #     )
        # )
        print("player_get_status:\n", await mina_service.player_get_status(device_id))
        # sleep(10)
        # print("player_stop:\n", await mina_service.player_stop(device_id))
        # print("player_get_status:\n", await mina_service.player_get_status(device_id))


if __name__ == "__main__":
    try:
        load_dotenv(find_dotenv(".env.test"))
    except ImportError:
        pass

    asyncio.run(main())
