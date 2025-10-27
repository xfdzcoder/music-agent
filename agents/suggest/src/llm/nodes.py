from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig

from base.core.src.langfuse_manager import langfuse, langfuse_handler

from llm.llm import deepseek
from model.model import MusicInfoList
from base.core.src.graph import State


def suggest(state: State) -> State:
    music_info = state["music_info_list"].root.pop()
    prompt = langfuse.get_prompt("suggest", label="latest", type="chat")
    langchain_prompt = ChatPromptTemplate(
        prompt.get_langchain_prompt(),
        metadata={"langfuse_prompt": prompt}
    )
    structured_llm = deepseek.with_structured_output(MusicInfoList, method='json_mode')
    chat_chain = langchain_prompt | structured_llm
    music_info_list: MusicInfoList = chat_chain.invoke(
        {"name": music_info.name, "author": music_info.author, "count": 1},
        config=RunnableConfig(callbacks=[langfuse_handler])
    )
    return {
        "messages": [
            AIMessage(content=f"我为你找到了{len(music_info_list.root)}首歌")
        ],
        "music_info_list": music_info_list
    }
