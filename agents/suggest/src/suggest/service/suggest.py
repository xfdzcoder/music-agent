from langchain_core.runnables import RunnableConfig

from core.graph.graph import SuggestState
from core.langfuse.langfuse_manager import langfuse_handler
from suggest.llm.graph import graph
from core.model.model import MusicInfo, MusicInfoList


def suggest_by_one(music_info: MusicInfo):
    state = SuggestState(messages=[], input_music_list=MusicInfoList(root=[music_info]))
    return _graph.invoke(
        state,
        config=RunnableConfig(callbacks=[langfuse_handler]),
    )
