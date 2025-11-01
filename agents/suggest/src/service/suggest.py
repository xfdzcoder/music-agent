from langchain_core.runnables import RunnableConfig

from base.core.src.graph import State, SuggestState
from base.core.src.langfuse_manager import langfuse_handler
from llm.graph import graph
from model.model import MusicInfo, MusicInfoList


def suggest_by_one(music_info: MusicInfo):
    state = SuggestState(messages=[], input_music_list=MusicInfoList(root=[music_info]))
    return graph.invoke(
        state,
        config=RunnableConfig(callbacks=[langfuse_handler]),
    )
