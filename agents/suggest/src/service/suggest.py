from langchain_core.prompts import ChatPromptTemplate

from llm.llm import llm
from model.model import MusicInfo, MusicInfoList
from service.langfuse import langfuse, langfuse_handler


def suggest_by_one(music_info: MusicInfo):
    prompt = langfuse.get_prompt("suggest", label="latest", type="chat")
    langchain_prompt = ChatPromptTemplate(
        prompt.get_langchain_prompt(),
        metadata={"langfuse_prompt": prompt}
    )
    structured_llm = llm.with_structured_output(MusicInfoList, method='json_mode')
    chat_chain = langchain_prompt | structured_llm
    return chat_chain.invoke(
        {"name": music_info.name, "author": music_info.author, "count": 10},
        config={"callbacks": [langfuse_handler]}
    )
