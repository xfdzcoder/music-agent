from typing import Annotated

from pydantic import BaseModel
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from model.model import MusicInfoList


class State(TypedDict):
    messages: Annotated[list, add_messages]
    music_info_list: MusicInfoList