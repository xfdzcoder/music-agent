from langchain_core.runnables import RunnableConfig

from base.core.src.graph import State
from base.core.src.langfuse_manager import langfuse_handler
from llm.graph import graph
from model.model import MusicInfo, MusicInfoList


async def suggest_by_one(music_info: MusicInfo):
    state = State(messages=[], music_info_list=MusicInfoList(root=[music_info]))
    for chunk in graph.invoke(state,
                              config=RunnableConfig(callbacks=[langfuse_handler]),
                              stream_mode="updates"):
        yield str(chunk)
