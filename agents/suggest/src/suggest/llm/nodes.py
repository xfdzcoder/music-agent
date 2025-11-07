from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig

from core.langfuse.langfuse_manager import langfuse, langfuse_handler

from core.llm.llm import deepseek
from suggest.llm.tools import check_exist_library
from core.model.model import MusicInfoList
from core.graph.graph import SuggestState


def suggest(state: SuggestState) -> SuggestState:
    music_info = state.input_music_list.root[0]
    prompt = langfuse.get_prompt("suggest", label="latest", type="chat")
    langchain_prompt = ChatPromptTemplate(
        prompt.get_langchain_prompt(),
        metadata={"langfuse_prompt": prompt}
    )
    structured_llm = deepseek.with_structured_output(MusicInfoList, method='json_mode')
    chat_chain = langchain_prompt | structured_llm
    output: MusicInfoList = chat_chain.invoke(
        {"name": music_info.name, "author": music_info.author, "count": state.get_target_count()},
        config=RunnableConfig(callbacks=[langfuse_handler]),
    )
    state.output_music_list = MusicInfoList.add_music_info_list(state.output_music_list, output)
    return state


def filter_existing(state: SuggestState) -> SuggestState:
    all_music = state.output_music_list.root
    filtered_music = [music for music in all_music if not check_exist_library(music)]
    remaining_count = 10 - len(filtered_music)
    is_done = remaining_count <= 0

    state.is_done = is_done
    state.output_music_list = MusicInfoList(root=filtered_music)
    state.target_count = remaining_count
    return state
