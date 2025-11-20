import asyncio
from typing import Any, List, Annotated

from langchain.agents import create_agent
from pydantic import BaseModel

from dotenv import load_dotenv, find_dotenv
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from chat.llm.graph import init_graph
from chat.llm.tools import search_music_info_by_title
from chat.service.music import aload_local_music
from core.db.postgres import init_db, run_migrations
from core.llm.langfuse.langfuse_manager import get_prompt
from core.llm.langfuse.prompt_param import PromptParam
from core.llm.llm import deepseek
from core.llm.memory.postgres import init_memory
from core.logger.logger import logger


class ChatState(BaseModel):
    messages: Annotated[List[Any], add_messages]


def main():
    graph_builder = StateGraph(ChatState)

    def chat(state: ChatState):
        agent = create_agent(deepseek, [search_music_info_by_title])
        langchain_prompt = get_prompt(
            "chat/chat",
            type="chat",
            messages_history=[],
            memories=[]
        )
        messages: list[BaseMessage] = langchain_prompt.invoke(
            input=PromptParam(input=state.messages[-1].content).model_dump(),
        ).to_messages()

        for chunk in agent.stream(
                input={ # noqa
                    "messages": messages
                },
                stream_mode=["messages", "updates"]
                # stream_mode=["updates"]
        ):
            print("CHUNK:", chunk, end="\n===\n\n")

    graph_builder.add_node(chat.__name__, chat)
    graph_builder.add_edge(START, chat.__name__)
    graph_builder.add_edge(chat.__name__, END)

    graph = graph_builder.compile()

    for event in graph.stream(
            input=ChatState(messages=[HumanMessage(content="《于是》这首歌的最后一句歌词是什么？")]),
            stream_mode=["messages", "updates", "values"]
    ):
        print("STREAM EVENT:", event, end="\n===\n\n")


if __name__ == "__main__":
    try:
        load_dotenv(find_dotenv(".env.test"))
    except ImportError:
        pass
    logger.info("Starting up...")
    init_db()
    run_migrations()
    init_memory()
    init_graph()
    asyncio.run(aload_local_music())
    main()

