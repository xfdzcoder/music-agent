import asyncio
from typing import Any, List, Annotated

from langgraph.config import get_stream_writer
from pydantic import BaseModel

from dotenv import load_dotenv, find_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessageChunk, \
    message_chunk_to_message
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


class ChatState(BaseModel):
    messages: Annotated[List[Any], add_messages]


async def main():
    graph_builder = StateGraph(ChatState)

    async def chat(state: ChatState):
        deepseek = init_chat_model(model="deepseek-chat", model_provider="deepseek")

        # 自己创建一个变量用来收集 AI 响应的 Chunk
        message_chunk : AIMessageChunk = AIMessageChunk(content="")
        async for chunk in deepseek.astream(state.messages):
            print("CHUNK:", chunk)
            get_stream_writer()
            message_chunk += chunk


        print("STATE: ", state)
        message = message_chunk_to_message(message_chunk)
        print("MESSAGE:", message)
        yield {
            "messages": [message],
        }

    graph_builder.add_node(chat.__name__, chat)
    graph_builder.add_edge(START, chat.__name__)
    graph_builder.add_edge(chat.__name__, END)

    graph = graph_builder.compile()

    async for event in graph.astream(
            input=ChatState(messages=[HumanMessage(content="Hello, world!")]),
            stream_mode=["messages", "updates", "values"]
    ):
        print("STREAM EVENT:", event)


if __name__ == "__main__":
    try:
        load_dotenv(find_dotenv(".env.test"))
    except ImportError:
        pass
    asyncio.run(main())
