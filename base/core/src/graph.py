from typing import Annotated

from pydantic import BaseModel
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from model.model import MusicInfoList


class State(BaseModel):
    messages: Annotated[list, add_messages] = Field(default_factory=list)
    is_done: bool = False


class SuggestState(State):
    input_music_list: MusicInfoList = Field(default_factory=MusicInfoList)
    output_music_list: MusicInfoList = Field(default_factory=MusicInfoList)
    target_count: int = 10

    def get_target_count(self):
        return 10 if self.target_count is None else self.target_count
