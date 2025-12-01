import requests

from core.config import config


def get_cover(album: str, artist: str) -> bytes:
    base_url = config.get_env("LRC_API_BASE_URL")
    response = requests.get(f"{base_url}/cover", params={"album": album, "artist": artist })
    return response.content